#!/usr/lib/env python
# -*- mode:python; coding:utf-8; -*-
# author: Darya Malyavkina <dmalyavkina@cloudlinux.com>
# created: 2017-03-30
# description:

import git
import logging
import os
import selenium
import sys
import time
import requests
from requests.auth import HTTPBasicAuth

from selenium import webdriver

KERNEL_VER = 'kernel-rt-3.8.13-rt14.20.el6rt'
URL_PATCHES = 'https://access.redhat.com/labs/psb/versions/{}/patches/%s?raw=true'.format(KERNEL_VER)
URL_PATCHES_LIST = 'https://access.redhat.com/labs/psb/versions/{}/patches'.format(KERNEL_VER)
REMOTE_URL = 'ssh://dmalyavkina@gerrit.cloudlinux.com:29418/patches-downloader'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def log_in():
    driver = webdriver.PhantomJS()
    driver.get("https://www.redhat.com/wapps/sso/login.html")
    time.sleep(3)
    driver.find_element_by_id("username").send_keys("dmalyavkina@cloudlinux.com")
    driver.find_element_by_id("password").send_keys("05Anivis+2592")
    driver.find_element_by_id("_eventId_submit").click()
    time.sleep(3)
    logger.info('Authorization succeeded in your account')
    return driver


def get_list_of_patches_names():
    driver = log_in()
    driver.get(URL_PATCHES_LIST)
    time.sleep(5)
    patches_list = []

    try:
        table_id = driver.find_element_by_class_name("table-files")
        rows = table_id.find_elements_by_tag_name("tr")
        count_rows = rows[1].find_element_by_class_name("num").text
        count_click = int(count_rows) / 50

        logger.info('Available %s patches' % count_rows)
        logger.info('Get a complete list of patch names')

        for i in range(count_click):
            driver.find_element_by_id("psb-load-more-patches").click()
            time.sleep(2)

    except Exception:
        logger.error('A non-existent version of the kernel is specified')

    logger.info('A full list of patches has opened')

    table_id = driver.find_element_by_class_name("table-files")
    rows = table_id.find_elements_by_tag_name("tr")

    for row in rows:
        patch_name = row.find_element_by_class_name("name").text
        if patch_name != '' and patch_name != "Name":
            patches_list.append(patch_name)

    logger.info('Created a list of patches names %s' % str(len(patches_list)))
    return patches_list


def download_patches_from_redhat():
    if not os.path.exists(KERNEL_VER):
        os.makedirs(KERNEL_VER)

    patches_list = get_list_of_patches_names()

    counter_created_file = 0

    logger.info('Started create files')

    for patch_name in patches_list:
        url = URL_PATCHES % patch_name

        patch_url = requests.get(url, auth=HTTPBasicAuth('dmalyavkina@cloudlinux.com', '05Anivis+2592'))
        patch = patch_url.text

        if patch:
            f = open('%s/%s.patch' % (KERNEL_VER, patch_name), 'w')
            f.write(patch.encode('utf-8'))
            f.close()

        counter_created_file += 1

        if not counter_created_file % 50:
            remains_patches = len(patches_list) - counter_created_file
            logger.info('Created {} files. '
                        'It remains to process {} files'.format(counter_created_file,
                                                                remains_patches))


def get_list_of_patches_names11111111111111():
    import pdb; pdb.set_trace()
    text = requests.get(URL_PATCHES_LIST, auth=HTTPBasicAuth('dmalyavkina@cloudlinux.com', '05Anivis+2592'))

    f = open('url_text.html', 'w')
    f.write(text.text.encode('utf-8'))
    f.close()

    logger.info('Created a list of patches names')
    #return patches_list


def main():
    download_patches_from_redhat()
    #get_list_of_patches_names()

if __name__ == '__main__':
    main()
