from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserRegistraterForm, UserUpdateForm, ProfileUpdateForm, LinkCustomerReceiptsForm
import os
from .models import users_db, Profile, registered_users_db, deposit_refund_transfers_db
import json
from datetime import datetime
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY




def register(request):
    if request.method == 'POST':
        form = UserRegistraterForm(request.POST)
        if form.is_valid():
            form.save()  # Automatically saves the user, hashes password etc in background
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Your account {username} has now been created! You are now able to login')
            return redirect('login')
    else:
        form = UserRegistraterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required(login_url='/login')  # Using a 'decorator' to add funcationallity to our views
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            username = u_form.cleaned_data.get('username')
            if p_form.has_changed():
                old_img_path = p_form['image'].initial.path
                if os.path.exists(old_img_path):
                    os.remove(old_img_path)
                else:
                    print("no path found print statement to show")
                    pass
            p_form.save()
            messages.success(request,  f'Your profile {username} has been updated!')
            return redirect('profile')
    else:
        current_user = request.user
        current_profile = Profile.objects.get(user=current_user.id)
        try:
            linked_account_details = users_db.objects.filter(EXTERNAL_ID__exact=current_profile.beandrop_social_user_uuid, EXTERNAL_TYPE__exact="DJANGO_USER").using('customer_data')[0]
            current_profile.beandrop_user_funds = linked_account_details.user_funds
            current_profile.beandrop_cups_in_ownership = linked_account_details.cups_owned
            #current_user_BeanDropProfile.beandrop_number_of_cups_used
            current_profile.save()
        except Exception as e:
            print("Error occured looking up details of current user in BD main database. Error was: ", e)

        
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)


def stripe_dash_redirect(request):
    try:
        current_user = request.user
        current_profile = Profile.objects.get(user=current_user.id)
        updated_registered_user = registered_users_db.objects.filter(EXTERNAL_ID__exact=current_profile.beandrop_social_user_uuid, EXTERNAL_TYPE__exact="DJANGO_USER").using('customer_data')[0]
    except Exception as e:
        print("Exception occured retrieving user in registered users. Exception was:", e)
        messages.warning(request,'To request a refund, you must link your account to a Bean Drop purchase. You can do this my entering your unique codes on your receipt.')
        return redirect('link_customer_receipts')
    else:
        try:
            stripe_login_link = stripe.Account.create_login_link(updated_registered_user.PAYMENT_ID)
            json_stripe_login_link = json.loads(str(stripe_login_link))
            return redirect(json_stripe_login_link['url'])
        except Exception as e:
            print("Error occured generating stripe login link. Exception was: ", e)
            messages.warning(request,'Oops an error occured generating a sign in link with stripe. Please try again. If this problem persits, please contact support.')

@login_required(login_url='/login')  # Using a 'decorator' to add funcationallity to our views
def link_customer_receipts(request):
    if request.method == 'POST':
        form = LinkCustomerReceiptsForm(request.POST)
        if form.is_valid():
            customer_qr_code = form.cleaned_data.get('customer_qr_code')
            customer_secret_code = form.cleaned_data.get('customer_secret_code')
            try:
                #all_entries = users_db.objects.all().using('customer_data')
                #print(all_entries)
                linked_account = users_db.objects.filter(QR_generator__exact=customer_qr_code, POS_generator__exact=customer_secret_code).using('customer_data')[0]
                print(linked_account)
                current_user = request.user
                current_profile = Profile.objects.get(user=current_user.id)
                linked_account.EXTERNAL_ID=current_profile.beandrop_social_user_uuid
                linked_account.EXTERNAL_TYPE="DJANGO_USER"
                linked_account.save()
                try:
                    currently_registered_on_bd_database = registered_users_db.objects.filter(EXTERNAL_ID__exact=current_profile.beandrop_social_user_uuid, EXTERNAL_TYPE__exact="DJANGO_USER").using('customer_data')[0]
                except Exception as e:
                    print("Found no user in registered_users_db matching, adding new user. Error was: ",e)
                    u = registered_users_db(EXTERNAL_ID=current_profile.beandrop_social_user_uuid, EXTERNAL_TYPE="DJANGO_USER")
                    u.save(using='customer_data')
                    print("new user added successfully to registered_users_db")
            except Exception as e:
                print("error occured with update of users_db when linking receipts to customer accounts, error was: ",e)
                messages.warning(request,'Error: We were unable to link your customer receipt to your account. Please check that you have submitted the correct codes, before pressing submit again.')
            else:
                messages.success(request,'Your account has now been updated and linked with your receipt! Cups and deposits have been updated in your account.')
                return redirect('profile')           
    else:
        form = LinkCustomerReceiptsForm()
    return render(request, 'users/link_customer_receipts.html', {'form': form})


@login_required(login_url='/login')  # Using a 'decorator' to add funcationallity to our views
def request_deposit_refund(request):
    if request.method == 'POST':
        connected_stripe_account = False
        #Determine if registered user is connected to a receipt account yet
        try:
            current_user = request.user
            current_profile = Profile.objects.get(user=current_user.id)
            updated_registered_user = registered_users_db.objects.filter(EXTERNAL_ID__exact=current_profile.beandrop_social_user_uuid, EXTERNAL_TYPE__exact="DJANGO_USER").using('customer_data')[0]
        except Exception as e:
            print("Exception occured retrieving user in registered users. Exception was:", e)
            messages.warning(request,'To request a refund, you must link your account to a Bean Drop purchase. You can do this my entering your unique codes on your receipt.')
            return redirect('link_customer_receipts')
        else:
            # Determine if they have any deposits to refund.
            linked_account = users_db.objects.filter(EXTERNAL_ID__exact=current_profile.beandrop_social_user_uuid, EXTERNAL_TYPE__exact="DJANGO_USER").using('customer_data')[0]
            if linked_account.user_funds <= 0:
                messages.warning(request,'You currently have no deposits to refund, return Bean Drop Cups to Bean Drop stations to have funds credited back into your account.')
            else:
                if updated_registered_user.PAYMENT_ID != "":
                    try: 
                        retrieved_stripe_account = stripe.Account.retrieve(updated_registered_user.PAYMENT_ID)
                    except Exception as e:
                        print("Retrieval of stripe account caused an exception. Exception is: ")
                        connected_stripe_account = False                        
                    else:
                        # Check if stripe account has completed onboarding and payments are setup.
                        json_retrieved_stripe_account = json.loads(str(retrieved_stripe_account))
                        if json_retrieved_stripe_account['charges_enabled'] == True:
                            connected_stripe_account = True
                            print("Charges enabled")
                        else:
                            connected_stripe_account = False
                            messages.warning(request, 'Please complete the onboarding process and add your chosen bank details to your stripe account to allow a successful deposit refund')
                            # Redirect user to complete onboarding process


                # Determine if user currently has connected stripe account
                if not connected_stripe_account:
                    return redirect('setup_payment_account')
                else:
                    # Determine value of deposit to be refunded.
                    refund_value = int(linked_account.user_funds)
                    stripe_refund_value = 100 * refund_value
                    print("Value to be refunded: £", refund_value)
                    # Update main users_db
                    linked_account.user_funds =  0
                    linked_account.save(using='customer_data')

                    try:
                        # Process Refund through Stripe
                        customer_deposit_refund_transfer_request = stripe.Transfer.create(
                            amount=stripe_refund_value,
                            currency="gbp",
                            destination=json_retrieved_stripe_account['id'],
                            )
                    except Exception as e:
                        print("Exception occurred during transfer request. Exception was: ", e)
                        # Roll back operation for database
                        linked_account.user_funds = refund_value
                        linked_account.save(using='customer_data')
                    else:
                        # Register transfer with main database
                        json_customer_deposit_refund_transfer_request = json.loads(str(customer_deposit_refund_transfer_request))
                        dt_transfer=datetime.fromtimestamp(json_customer_deposit_refund_transfer_request['created'])
                        new_refund_transfer = deposit_refund_transfers_db(
                            registered_user_id=current_profile.beandrop_social_user_uuid, 
                            registered_user_external_type="DJANGO_USER",
                            users_db_qr_generator=linked_account.QR_generator,
                            transfer_id=json_customer_deposit_refund_transfer_request['id'],
                            transfer_value=refund_value,
                            transfer_datetime=dt_transfer
                            )
                        new_refund_transfer.save(using='customer_data')

                        #return redirect successful transfer
                        messages.success(request, "We've successfully processed your refund, your bank should receive payment within 72 hours.")
                        return redirect('profile')

    else:
        pass
        #form = LinkCustomerReceiptsForm()
    return render(request, 'users/request_deposit_refund.html')

@login_required(login_url='/login')  # Using a 'decorator' to add funcationallity to our views
def setup_payment_account(request):
    if request.method == 'POST':
        connected_stripe_account = False
        #Determine if registered user is connected to a receipt account yet
        try:
            current_user = request.user
            current_profile = Profile.objects.get(user=current_user.id)
            updated_registered_user = registered_users_db.objects.filter(EXTERNAL_ID__exact=current_profile.beandrop_social_user_uuid, EXTERNAL_TYPE__exact="DJANGO_USER").using('customer_data')[0]
        except Exception as e:
            print("Exception occured retrieving user in registered users. Exception was:", e)
            messages.warning(request,'To request a refund, you must link your account to a Bean Drop purchase. You can do this my entering your unique codes on your receipt.')
            return redirect('link_customer_receipts')
        else:
            if updated_registered_user.PAYMENT_ID != "":
                try: 
                    retrieved_stripe_account = stripe.Account.retrieve(updated_registered_user.PAYMENT_ID)
                except Exception as e:
                    print("Retrieval of stripe account caused an exception. Exception is: ")
                    connected_stripe_account = False
                else:
                    stripe_user_id = updated_registered_user.PAYMENT_ID
                    connected_stripe_account = True

            # Determine if user currently has connected stripe account
            if not connected_stripe_account:
                new_stripe_user = stripe.Account.create(
                    country="GB",
                    type="express",
                    capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True}},
                    business_type="individual",
                    business_profile={"url": 'https://beandrop.net/profile'},
                    )
                print("Result of creating new stripe connect user: ",new_stripe_user)
                json_new_stripe_user = json.loads(str(new_stripe_user))
                print("Extracted Json data below")
                print(json_new_stripe_user['id'])
                # Register id in main bd database.
                current_user = request.user
                current_profile = Profile.objects.get(user=current_user.id)
                updated_registered_user = registered_users_db.objects.filter(EXTERNAL_ID__exact=current_profile.beandrop_social_user_uuid, EXTERNAL_TYPE__exact="DJANGO_USER").using('customer_data')[0]
                updated_registered_user.PAYMENT_ID = json_new_stripe_user['id']
                updated_registered_user.save(using='customer_data')
                print("successfully added payment id to registered_users_db")
                # Generate account link and redirect user to account link URL
                stripe_user_id = json_new_stripe_user['id']

            #Creating account link to Stripe and redirecting with provided url   
            stripe_account_link = stripe.AccountLink.create(
                account=stripe_user_id,
                refresh_url="https://beandrop.net/request_deposit_refund",  #https://beandrop.net/request_deposit_refund
                return_url="https://beandrop.net/request_deposit_refund",    #https://beandrop.net/users/profile
                type="account_onboarding",
                )
            json_stripe_account_link = json.loads(str(stripe_account_link))
            return redirect(json_stripe_account_link['url'])
    else:
        pass
        #form = LinkCustomerReceiptsForm()
    return render(request, 'users/setup_payment_account.html')
