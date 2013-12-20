==========================
robotframework-imaplibrary
==========================

**robotframework-imaplibrary** is a `Robot Framework
<http://code.google.com/p/robotframework/>`_ test library to test
mail validation tasks.

Installation
++++++++++++

To install, just fetch the latest version from PyPI:.

    pip install --upgrade robotframework-imaplibrary

Usage
+++++

Setup in the robotframework Settings section:

============  ================
  Setting          Value
============  ================
Library          ImapLibrary
============  ================

\

These keyword actions are available::

    Open Mailbox:
        Open the mailbox on a mail server with a valid authentication:
        Arguments:
            - server:   the server name (e.g. imap.googlemail.com)
            - user:     the user name (e.g. me@googlemail.com)
            - password: the user's password

    Wait for Mail:
        Wait for an incoming mail. Check the mailbox every 10 seconds
        for incoming mails until a matching email is received or the
        timeout is exceeded. Returns the mail number of the latest matching
        email.
        Arguments:
            - fromEmail: the email address of the sender (not required)
            - toEmail:   the email address of the receiver (not required)
            - status:    the status of the email (not required)
            - timeout:   the timeout how long the mailbox shall check emails
                         in seconds (defaults to 60 seconds)

    Get Links From Email:
        Finds all links in an email body and returns them

        Arguments:
            - mailNumber: is the index number of the mail to open

    Get Matches From Email:
        Finds all occurrences of a regular expression

        Arguments:
            - mailNumber: is the index number of the mail to open
            - regexp: a regular expression to find

    Open Link from Mail:
        Find a link in an email body and open the link. Returns the links' html.
        Arguments:
            mailNumber: the number of the email to check for a link
            linkNumber: the index of the link to open
                        (defaults to 0, which is the first link)

    Get Email body:
        Returns an email body
        Arguments:
            mailNumber: the number of the email to check for a link

    Walk Multipart Email
        Returns the number of parts of a multipart email. Content is stored internally
        to be used by other multipart keywords. Subsequent calls iterate over the
        elements, and the various Get Multipart keywords retrieve their contents.

        Arguments:
            mailNumber: the index number of the mail to open

    Get Multipart Content Type
        Return the content-type for the current part of a multipart email

    Get Multipart Payload
        Return the payload for the current part of a multipart email

        Arguments:
            decode: an optional flag that indicates whether to decoding

    Get Multipart Field Names
        Return the list of header field names for the current multipart email

    Get Multipart Field
        Returns the content of a header field 

        Arguments:
            field: a string such as 'From', 'To', 'Subject', 'Date', etc.

    Mark as read:
        Mark all received mails as read

    Close Mailbox:
        Close the mailbox after finishing all mail activities of a user.

For more informaiton on `status` see: `Mailbox Status <http://pymotw.com/2/imaplib/#mailbox-status>`_.

Here is an example of how to use the library:

==============  ==========================  ===================================  ==================================  =============  ============
 Action         Argument                    Argument                             Argument                            Argument       Argument
==============  ==========================  ===================================  ==================================  =============  ============
Open Mailbox    server=imap.googlemail.com  user=mymail@googlemail.com           password=mysecretpassword
${LATEST}=      Wait for Mail               fromEmail=noreply@register.com       toEmail=mymailalias@googlemail.com  status=UNSEEN  timeout=150
${HTML}=        Open Link from Mail         ${LATEST}
Should Contain  ${HTML}                     Your email address has been updated
Close Mailbox
==============  ==========================  ===================================  ==================================  =============  ============

Here is an example of how to work with multipart emails, ignoring all non content-type='test/html' parts:

==============  ==========================  ===================================  ===================================  ============
 Action         Argument                    Argument                             Argument                             Argument
==============  ==========================  ===================================  ===================================  ============
Open Mailbox    server=imap.googlemail.com  user=mymail@googlemail.com           password=mysecretpassword
${LATEST}=      Wait for Mail               fromEmail=noreply@register.com       toEmail=mymailalias@googlemail.com   timeout=150
${parts}=       Walk Multipart Email        ${LATEST}
@{fields}=      Get Multipart Field Names
${from}=        Get Multipart Field         From
${to}=          Get Multipart Field         To
${subject}=     Get Multipart Field         Subject
:FOR            ${i}                        IN RANGE                             ${parts}
\               Walk Multipart Email        ${LATEST}
\               ${content-type}=            Get Multipart Content Type
\               Continue For Loop If        '${content-type}' != 'text/html'
\               ${payload}=                 Get Multipart Payload                decode=True
\               Should Contain              ${payload}                           Update your email address
\               ${HTML}=                    Open Link from Mail                  ${LATEST}
\               Should Contain              ${HTML}                              Your email address has been updated
Close Mailbox
==============  ==========================  ===================================  ===================================  ============

License
+++++++

The robotframework-imaplibrary is licensed under the `Apache 2.0 License
<http://www.apache.org/licenses/LICENSE-2.0.html>`_.
