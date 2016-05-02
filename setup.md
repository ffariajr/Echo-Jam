# Setup

#### This file describes how Echo Jam [is set up](#configuration), and how to set up Echo Jam [by yourself.](#walkthrough)

<a name="configuration" />
## Configuration



<a name="walkthrough" />
## Setup Walkthrough

First, go to Amazon Web Services ([AWS](https://aws.amazon.com)) and sign in to the console.
Click on Lambda, and then **Create a Lambda Function**.
Scroll to the right in the list of template functions until you find **alexa-skills-kit-color-expert-python**.  Make sure the bottom of the box reads *python2.7*.
Leave **Event Source Type** as *Alexa Skills Kit*
Name your new Lambda function *EchoJam*, and add a description.
It is easiest to just paste the code from [lambdacode.py](https://github.com/ffariajr/Echo-Jam/blob/master/lambdacode.py) into the code section.
Under **Role**, choose *Basic Execution Role*.  You will be brought to a new window/tab where the only thing you need to click is **Allow**.
Click **Next**.  Click **Create Function**.
On the top right, highlight and copy the **ARN**, the part that comes after "ARN - ".

Now we will switch gears to configure Alexa's servers to send transcribed text to our lambda function.

Sign in to Amazon's Developer site at https://developer.amazon.com.
Once signed in, navigate to the **Alexa** tab and then click **get started** under **Alexa Skills Kit**.
You will be brought to a screen that lists your current **Alexa Skills Kit** apps.  Click **Add a New Skill**.

Give your new skill the name *Echo Jam* and for the **invocation name**, use *echo jam*.  Note the upper/lower case.
Click Next.
Then look at the left side navigation menu and click **Configuration**.
Select the **Lambda ARN (Amazon Resource Name)** bullet, and paste in the Lambda ARN which should still be in your clipboard.
Select *No* for **Account Linking**.
Click **Save**, and then click **Interaction Model** in the left side navigation menu. This is where you will paste in the *Intent Schema*, *Custom Slot Values*, and *Sample Utterances* from the respective files in the [config](https://github.com/ffariajr/Echo-Jam/blob/master/config) folder.  Remember to click *save*.  It will take some time for Alexa to update her *interaction model*.

#### Your new Alexa Skill is complete. You may use [Amazon's documentation on Alexa](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit#get-started-now) for help in modifying the code.
