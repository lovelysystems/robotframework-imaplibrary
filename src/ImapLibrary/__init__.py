import re
import os
import imaplib
import time
import urllib2
import email

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
execfile(os.path.join(THIS_DIR, 'version.py'))

__version__ = VERSION


class ImapLibrary(object):

    ROBOT_LIBRARY_VERSION = VERSION
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    port = 993

    def open_mailbox(self, server, user, password):
        """
        Open the mailbox on a mail server with a valid
        authentication.
        """
        self.imap = imaplib.IMAP4_SSL(server, self.port)
        self.imap.login(user, password)
        self.imap.select()
        self._init_walking_multipart()

    def wait_for_mail(self, fromEmail=None, toEmail=None, status=None,
                      timeout=60):
        """
        Wait for an incoming mail from a specific sender to
        a specific mail receiver. Check the mailbox every 10
        seconds for incoming mails until the timeout is exceeded.
        Returns the mail number of the latest email received.

        `timeout` sets the maximum waiting time until an error
        is raised.
        """
        timeout = int(timeout)
        while (timeout > 0):
            self.mails = self._check_emails(fromEmail, toEmail, status)
            if len(self.mails) > 0:
                return self.mails[-1]
            timeout -= 10
            if timeout > 0:
                time.sleep(10)
        raise AssertionError("No mail received within time")

    def get_links_from_email(self, mailNumber):
        '''
        Finds all links in an email body and returns them

        `mailNumber` is the index number of the mail to open
        '''
        body = self.get_email_body(mailNumber)
        return re.findall(r'href=[\'"]?([^\'" >]+)', body)

    def get_matches_from_email(self, mailNumber, regexp):
        """
        Finds all occurrences of a regular expression
        """
        body = self.get_email_body(mailNumber)
        return re.findall(regexp, body)

    def open_link_from_mail(self, mailNumber, linkNumber=0):
        """
        Find a link in an email body and open the link.
        Returns the link's html.

        `mailNumber` is the index number of the mail to open
        `linkNumber` declares which link shall be opened (link
        index in body text)
        """
        urls = self.get_links_from_email(mailNumber)

        if len(urls) > linkNumber:
            resp = urllib2.urlopen(urls[linkNumber])
            content_type = resp.headers.getheader('content-type')
            if content_type:
                enc = content_type.split('charset=')[-1]
                return unicode(resp.read(), enc)
            else:
                return resp.read()
        else:
            raise AssertionError("Link number %i not found!" % linkNumber)

    def close_mailbox(self):
        """
        Close the mailbox after finishing all mail activities of a user.
        """
        self.imap.close()

    def mark_as_read(self):
        """
        Mark all received mails as read
        """
        for mail in self.mails:
            self.imap.store(mail, '+FLAGS', '\SEEN')

    def get_email_body(self, mailNumber):
        """
        Returns an email body

        `mailNumber` is the index number of the mail to open
        """
        if self._is_walking_multipart(mailNumber):
            body = self.get_multipart_payload(decode=True)
        else:
            body = self.imap.fetch(mailNumber, '(BODY[TEXT])')[1][0][1].decode('quoted-printable')
        return body

    def walk_multipart_email(self, mailNumber):
        """
        Returns the number of parts of a multipart email. Content is stored internally
        to be used by other multipart keywords. Subsequent calls iterate over the
        elements, and the various Get Multipart keywords retrieve their contents.

        `mailNumber` is the index number of the mail to open
        """
        if not self._is_walking_multipart(mailNumber):
            data = self.imap.fetch(mailNumber, '(RFC822)')[1][0][1]
            msg = email.message_from_string(data.decode())
            self._start_walking_multipart(mailNumber, msg)

        try:
            self._part = next(self._mp_iter)
        except StopIteration:
            self._init_walking_multipart()
            return False
            
        # return number of parts
        return len(self._mp_msg.get_payload())

    def _is_walking_multipart(self, mailNumber):
        """
        Check if walking a multipart email is in progress
        """
        return self._mp_msg is not None and self._mailNumber == mailNumber

    def _start_walking_multipart(self, mailNumber, msg):
        self._mailNumber = mailNumber
        self._mp_msg = msg
        self._mp_iter = msg.walk()

    def _init_walking_multipart(self):
        self._mp_msg = None
        self._part = None
        self._mailNumber = None

    def get_multipart_content_type(self):
        """
        Return the content-type for the current part of a multipart email
        """
        return self._part.get_content_type()

    def get_multipart_payload(self, decode=False):
        """
        Return the payload for the current part of a multipart email

        decode is an optional flag that indicates whether to decoding
        """
        s = self._part.get_payload(decode=decode)
        charset = self._part.get_content_charset()
        if charset is not None:
            return s.decode(charset)
        return s

    def get_multipart_field_names(self):
        """
        Return the list of header field names for the current multipart email
        """
        return self._mp_msg.keys()

    def get_multipart_field(self, field):
        """
        Returns the content of a header field 

        field is a string such as 'From', 'To', 'Subject', 'Date', etc.
        """
        return self._mp_msg[field]

    def _criteria(self, fromEmail, toEmail, status):
        crit = []
        if fromEmail:
            crit += ['FROM', fromEmail]
        if toEmail:
            crit += ['TO', toEmail]
        if status:
            crit += [status]
        if not crit:
            crit = ['UNSEEN']
        return crit

    def _check_emails(self, fromEmail, toEmail, status):
        crit = self._criteria(fromEmail, toEmail, status)
        typ, msgnums = self.imap.search(None, *crit)
        if typ != 'OK':
            raise Exception('imap.search error: ' + typ + ', ' + str(msgnums) + ' criterion=' + str(crit))
        return msgnums[0].split()
