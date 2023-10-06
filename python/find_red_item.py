#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from lxml import html as H
from urlparse import urlparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass
import ConfigParser
import StringIO

#from lxml.html.builder import *

CFG = {}
FA_DICT = {
    'Pf-PreDR0' : 'RnDPrime',
    'Pf-DR0' : 'RnDPrime',
    'Pf-DR1' : 'RnDPrime',
    'Pf-Done'  : 'RnDPrime',
    'MiBDropDate'  : 'RnDPrime',
    'DBandMigDropDate' : 'RnDPrime',
    'CLIDropDate' : 'RnDPrime',
    'TL1DropDate' : 'RnDPrime',
    'SWDropDate' : 'RnDPrime',
    'ATCDropDate' : 'TestPrime',
    'ATCDelComment' : 'TestPrime',
    'EarlyTestInvolv' : 'TestPrime',
    'View/Update CCR Estimate' : 'RnDPrime',
    'FDT Binder' : 'RnDPrime',
    'Documentation Plan' : 'RnDPrime',
    'Feature Summary' : 'RnDPrime',
    'Architecture Document' : 'RnDPrime',
    'Master TestList' : 'RnDPrime',
    'Test Strategy' : 'TestPrime',
    'CustDocImpact' : 'ArchPrime'
}


f = open("fa.html", "r")
page = f.read()

root = H.fromstring(page)

#create new html frame
#red_html = lxml.html.Element("root")

# find all tr that are overdue

doctype = '<!doctype html public "-//w3c//dtd html 4.0 transitional//en">'
head = H.tostring(root[0])
table = root.xpath('./body/form/table[@class="sortable"]')
th = H.tostring(table[0][0])
#thead = table[0][0]

subject_msg = ' - quality metics red in FA RCR page. Please take action'

all_trs = table[0].xpath('./tr[@class="crw2_rw"]')

'''
red_trs_list = []
for tr in all_trs:
    red_td = tr.xpath('./td[@bgcolor="#FF0000"]')
    if red_td:
        red_trs_list.append(tr)
        continue
'''
red_trs_list = [tr for tr in all_trs if tr.xpath('./td[@bgcolor="#FF0000"]')]
'''
normal_trs_list = [tr for tr in all_trs if tr not in red_trs_list]
for tr in normal_trs_list:
    table[0].remove(tf)

root.write('output.html')
'''

def parsing_config():
    try:
        cf = ConfigParser.ConfigParser()
        cf.read('fa_check.cfg')

        sections = cf.sections()

        mail_options = cf.options("MAIL")
        url_options = cf.options("URL")
        template_options = cf.options("TEMPLATE")
        template_options = cf.options("DEBUG")
        CFG['mail_cc'] = cf.get("MAIL", "cc")
        CFG['mail_from'] = cf.get("MAIL", "from")
        CFG['cc_supervisor'] = cf.get("MAIL", "cc_supervisor")
        CFG['smtp'] = cf.get("MAIL", "smtp")
        CFG['url'] = cf.get("URL", "url")
        CFG['title_temp'] = cf.get("TEMPLATE", "title")
        CFG['testing_mode'] = cf.get("DEBUG", "testing_mode")
        if DEV_MODE == True:
            LOGGER.debug("mail_cc: %s" % CFG['mail_cc'])
            LOGGER.debug("mail_from: %s" % CFG['mail_from'])
            LOGGER.debug("smtp_server: %s" % CFG['smtp'])
            LOGGER.debug("cc_supervisor: %s" % CFG['cc_supervisor'])
            LOGGER.debug("url: %s: " % CFG['url'])
            LOGGER.debug("title_temp: %s" % CFG['title_temp'])
            LOGGER.debug("testing_mode: %s" % CFG['testing_mode'])
    #except ConfigParser.NoSectionError as e:
    except Exception as e:
        LOGGER.error( "Invalid overdue.cfg %s!" % e)
        raise
    else:
        pass
        #LOGGER.info( sections)
        #LOGGER.info( mail_options)
        #LOGGER.info( url_options)
        #LOGGER.info( template_options)
        #return (smtp, url, mail_cc, title_temp))


def find_key_of_cell(cell):
    for key in FA_DICT:
        if key in cell:
            return key
    return ''

def init_smtp_server():
    try:
        LOGGER.debug("smtp_server: %s" % CFG['smtp'])
        CFG['smtp'] = smtplib.SMTP(CFG['smtp'])
    except Exception as e:
        LOGGER.error("Cannot connect to smtp server %s" % CFG['smtp'])
        LOGGER.error(e)
        raise

def fc_config():
    parsing_config()
    init_smtp_server()

'''
def _get_email_addr(url):
    ''' return  a list including the mail from url and a url for supervisor
    as [email, url_of_boss]
    '''
    email_page = urllib2.urlopen(url).read()
    email_pattern = r'<a href="mailto:(.*?@.*?)\">.*?div_tree_up.*?><a href=\"(.*?)\">'
    try:
        find = re.compile(email_pattern, re.DOTALL).search(email_page)
        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    except AttributeError as e:
        LOGGER.error("Cannot find mail info! %s" % e)
    else:
        return [find.group(1), domain[:-1] + find.group(2)]


def get_email_addr(url):
    email = _get_email_addr(url)
    #print "email is: ", email
    #print "email[1] is ", email[1]
    boss_email = _get_email_addr(email[1])
    email[1] = boss_email[0]
    return [email[0], email[1]]
'''

def get_rcr_no(tr):
    return tr[0].xpath('./*/*/*/font')[0].text


def handle_red_tr(red_trs_list):
    '''
    return rcr
    rcr = {'no': 'xxxxx',
           'description': 'isamv ...',
           'overdue_tems': [overdued_item0, overdue_item1 ... ]
           'html': file-like object
          }


    overdued_item = [title : [{people0}, {people1}, ...]]
                              #one item might map to more than one people

                    people = {'role':, 'name':, 'mail':, 'boss_mail':}
                                       #item   #people
                                            |  |
                                            |  |
                      people0  #rcr('item')[0][0]
               people0's mail  #rcr('item')[0][0]('mail')

    '''
    rcr = []

    #for tr in red_trs_list[:2]: # to do
    for tr in all_trs_list: # to do
        red_td = tr.xpath('./td[@bgcolor="#FF0000"]')
        if red_td:
            rcr = {}
            rcr['no'] = tr[0].xpath('./*/*/*/font')[0].text
            rcr['description'] = tr[1].xpath('./a[@title="Show RCR Binder"]/small')[0].text
            rcr['item'] = []
            for _td in red_td:
                _title = _td.xpath('./a')[0].get('title')
                # get [{people0], {people1}...]
                people = find_people_by_title(_td, _title)
                rcr['item'].append(people)
                ## resume here
            html_str = generate_html(head, th, H.tostring(tr))
            #f = open("result.html", "w")
            #f.write(html)
            #f.close()
            #continue
            #f = StringIO.StringIO(html_str)
            rcr['html'] = generate_html(head, th, H.tostring(tr))



def find_people_by_title(td, title):
    '''Return a list including all related people with the arg td'''
    #FA_DICT's keys are shorter than title
    for item in FA_DICT.iteritems():
    # item is like ('EarlyTestInvolv', 'TestPrime')
        if item[0] in title:
            return find_people_by_prime(td.getparent(), FA_DICT[item[0]])
                                           # from the tr, getting ...


def find_people_by_prime(tr, role):
    '''Return a list including all cooresponding specific primes,
       sometimes, there are more than one ArchPrimes or RndPrimes.
       return [{people}... ]
       people = {'role':xxx, 'name':xxx, 'mail':xxx, 'boss_mail':xxx}
    '''
    primes = []
    #list of elemenet(s) of a specific Prime/role in a tr
    _xpath = './td/table/tr/td/a[@title="Filter on %s"]' % role
    # get all hrefs of the specific primes that might be more than one
    _primes = tr.xpath(_xpath)
    for _a in _primes:
        name = _a.xpath('./small')[0].text
        url = tr.xpath('./td/table/tr/td/a[@title="Show ZZZ Directory info for %s"]' % name)[0].get('href')
        mail_addr, boss_url = get_mail_by_url(url)
        #boss_mail_addr, boss_url = get_mail_by_url(url)
        boss_mail_addr, ignore = get_mail_by_url(boss_url,False)
        # audit here todo
        primes.append({"role" : role,
                       "name" : name,
                       "mail" : mail_addr,
                       "boss_mail": boss_mail_addr})
    return primes


def get_mail_by_url(url, find_boss=True):
    '''
    return  a list including the mail from url and a url for supervisor
    as [email, boss_url]
    '''
    email_page = urllib2.urlopen(url).read()
    eroot = H.fromstring(email_page)
    person_attr_names = eroot.xpath('//div[@class="person_attr_name"]')
    mail_addr = ''
    boss_url = ''
    person_attr_value = get_attr_value_by_name("Email:", person_attr_names)
    if person_attr_value is None:
        #error handler here todo
        print "cannot get_attr_value_by_name %s" % "Email:"
        print "email cannot be found by %s" % url
    else:
        mail_addr = person_attr_value.text
        if find_boss == True:
            # return a boss mail's url
            parsed_uri = urlparse(url)
            #[:-1] is for deleting the suffix '/'
            boss_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)[:-1]
            boss_ele = get_attr_value_by_name("Supervisor:", person_attr_names)
            boss_href = boss_ele.get('href')
            if not boss_href:
                print "supervisor's url cannot be found by %s" % url
            else:
                boss_url += boss_href
    return (mail_addr, boss_url)


def get_attr_value_by_name(person_attr_name, person_attr_names):
    '''Return the element of person_attr_value by person_attr_name'''
    for _name in person_attr_names:
        if _name.text.strip() == person_attr_name:
            return _name.getparent().xpath('./div/a')[0]

'''
def get_email_addr(url):
    email = _get_email_addr(url)
    #print "email is: ", email
    #print "email[1] is ", email[1]
    boss_email = _get_email_addr(email[1])
    email[1] = boss_email[0]
    return [email[0], email[1]]
'''


def generate_html(head, th, tr):
    html_str = doctype + '<html>\n' + head + '<body>\n'
    #hard code here,
    html_str += '<table class="sortable" border=1 cellspacing=0 width=100%>\n'
    html_str += th + tr
    html_str += '</table>\n</body>\n</html>'
    return html_str


def send_to_people(rcr, html, msg):
    ''' Translate rcr into a msg dict '''
    msg = MIMEMultipart('alternative')
    msg['Subject'] = rcr['no'] + rcr['description'] + msg_subject
    cc_list = CFG['mail_cc'] + ';'
    msg['From'] = CFG['mail_from'] + ';'
    to_list = ''
    for item in rcr['item']:
        for people in item:
            # enclosed by str(), since people['mail'} might be None that
            # cannot += with 'str'
            to_list += people['mail'] + ';'
            cc_list += people['boss_mail'] + ';'
            text = "Hi, %s\n Could you please correct the overdueness?" % peopel['role'] + 'of' + rcr['no']
            msg['Cc'] = cc_list
            msg['To'] = to_list
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            # resume here


#1. Generate a html with a head that retrieves from root
#red_html = HTML((HEAD(root.head)), BODY(TABLE(THEAD(thead), TBODY(red_trs_list[1]))))

red_html = lxml.html.Element("html")
>>lxml.html.tostring('html')
>>'<html></html>'
#head = red_html.SubElement(html, thread)
body = lxml.html.tostring(root[1])
