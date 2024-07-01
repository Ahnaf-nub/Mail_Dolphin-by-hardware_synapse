# Mail Dolphin Documentation
## Team Members:

* Mir Muhammad Abidul Haq (Ahnaf) - email: abidulhaqahnaf@gmail.com
* A. N. M. Noor - email: nafis.noor.202012@gmail.com
* Iqbal Samin Prithul - email: prithul0218@gmail.com

## Overview of our Repository
 * `static` - this folder contains the codes for client side.  
 * `templates` - this folder contains HTML template files.
 * `app.py` - This is the main code for flask part and also for tinyllama

### About our Project

**Problem Statement**
Managing and responding to emails can be time-consuming and overwhelming, especially when dealing with a high volume of incoming messages. It is often necessary to respond to emails promptly and in a personalized manner to maintain professional communication and ensure that important information is communicated in a timely manner. As a result, it is more difficult to understand the intent behind each email and respond appropriately based on individual preferences and contexts.

**Solution Overview**
To address this issue, we've developed an automated email reply system (Mail Dolphin) that leverages advanced natural language processing (NLP) and machine learning techniques. This system is designed to: Analyze Incoming Emails: The system scans and processes incoming emails to extract key information, such as sender details, subject lines, and the body of the email. It uses NLP to parse the content of the emails and identify relevant keywords, phrases, and contexts. Craft Personalized Replies Based on Your Preferences: The system generates customized replies that align with the user's communication style and preferences. It uses predefined templates and dynamically fills in the details based on the context of the incoming email. To ensure that the recipient feels valued and understood, the replies are carefully crafted to be professional, polite, and contextually appropriate. 

### Workflow
1. User integrates their existing Gmail account with Mail-Dolphin.
2. Adds some General information along with some example emails and replies to tune the service to match their preferences.
3. Mail-Dolphin checks for any email the user receives.
4. Generates a reply based on the information and examples given by the user.
5. Replies to the email on behalf of the user.

### Tech Stacks
We used,
* `Flask API` for the backend
* `Bootstrap`, `CSS`, and `HTML` for the interface
* `Javascript` for handling the communication between the frontend and the backend
* `Tinyllama` for NLP
* `Gmail API` to integrate user's Gmail with our Mail-Dolphin


## Usage
Tuning Mail-Dolphin is really easy!

First, add some general information about yourself / your company. Anything that would be needed for Mail-Dolphin in order to reply to emails on your behalf.
Go to the `Tune` page. Here, you'll find the customization wizard. Now add to the `General Information`.

![image](https://github.com/Ahnaf-nub/Mail_Dolphin-by-hardware_synapse/assets/113457396/76615fe6-62aa-4a82-9f9f-2efb03bc8b69)

Then, add some example replies that describe your desired tone. It is a good idea to add some examples based on frequently asked questions.
Inside the `Example replies` section, you can add, delete, or duplicate an example.

![image](https://github.com/Ahnaf-nub/Mail_Dolphin-by-hardware_synapse/assets/113457396/5d3fec31-3637-42db-b5cf-aba4c5c83431)
