#!/usr/lib/env python
# -*- mode:python; coding:utf-8; -*-
# author: Darya Malyavkina <dmalyavkina@cloudlinux.com>
# created: 2017-03-30
# description:

import git
import logging
import os
import sys
import time

from selenium import webdriver

KERNEL_VER = sys.argv[1]
URL_PATCHES = 'https://access.redhat.com/labs/psb/versions/{}/patches/%s?raw=true'.format(KERNEL_VER)
URL_PATCHES_LIST = 'https://access.redhat.com/labs/psb/versions/{}/patches'.format(KERNEL_VER)
REMOTE_URL = 'git@github.com:dshakhray/test_python.git'

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
    time.sleep(10)
    patches_list = []

    try:
        table_id = driver.find_element_by_class_name("table-files")
        rows = table_id.find_elements_by_tag_name("tr")
        count_rows = rows[1].find_element_by_class_name("num").text
        count_click = int(count_rows) / 50

        for i in range(count_click):
            driver.find_element_by_id("psb-load-more-patches").click()
            time.sleep(3)
    except Exception:
        pass

    logger.info('A full list of patches has opened')

    table_id = driver.find_element_by_class_name("table-files")
    rows = table_id.find_elements_by_tag_name("tr")

    for row in rows:
        patch_name = row.find_element_by_class_name("name").text
        if patch_name != '' and patch_name != "Name":
            patches_list.append(patch_name)

    logger.info('Created a list of patches names')
    return patches_list


def download_patches_from_redhat():
    if not os.path.exists(KERNEL_VER):
        os.makedirs(KERNEL_VER)
        patches_list = get_list_of_patches_names()
    else:
        patches_list = get_update_patches_names()

    driver = log_in()
    counter_created_file = 0

    logger.info('Started create files')

    for patch_name in patches_list:
        url = URL_PATCHES % patch_name
        driver.get(url)
        time.sleep(3)
        patch = driver.find_elements_by_tag_name("body")[0].text

        if patch == '':
            logger.info('Required re-authorize on the Red Hat account')
            driver = log_in()
            driver.get(url)
            patch = driver.find_elements_by_tag_name("body")[0].text

        f = open('%s/%s' % (KERNEL_VER, patch_name), 'w')
        f.write(patch.encode('utf-8'))
        f.close()

        counter_created_file += 1
        if not counter_created_file % 50:
            remains_patches = len(patches_list) - counter_created_file
            logger.info('Created {} files. '
                        'It remains to process {} files'.format(counter_created_file,
                                                                remains_patches))


def get_update_patches_names():
    patches_list = get_list_of_patches_names()
    patches_update = []

    for patch_name in patches_list:
        patch_path = '%s/%s' % (KERNEL_VER, patch_name)
        if not os.path.exists(patch_path):
            patches_update.append(patch_name)

    logger.info('A list of new patches has been created. '
                'You need to add {} patches'.format(len(patches_update)))
    return patches_update


def git_init():
    repo = git.Repo.init()

    if not repo.remotes:
        origin = repo.create_remote('origin',  url=REMOTE_URL)
    else:
        origin = repo.remotes.origin

    origin.pull('master')
    logger.info('Initialized Git repository. Repo is updated.')


def push_changes():
    repo = git.Repo.init()
    origin = repo.remotes.origin

    repo.index.add([KERNEL_VER])
    repo.index.commit("Add patches for %s" % KERNEL_VER)
    origin.push('master')
    logger.info('Patches added to %s' % KERNEL_VER)


def main():
    git_init()
    download_patches_from_redhat()
    push_changes()


if __name__ == '__main__':
    main()
