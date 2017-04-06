#!/usr/lib/env python
# -*- mode:python; coding:utf-8; -*-
# author: Darya Malyavkina <dmalyavkina@cloudlinux.com>
# created: 2017-03-30
# description:

from selenium import webdriver
import time
import git
import os
import logging

KERNEL_VER = 'kernel-rt-3.8.13-rt14.20.el6rt'#'kernel-3.10.0-514.el7'
URL_PATCHES = 'https://access.redhat.com/labs/psb/versions/{}/patches/%s?raw=true'.format(KERNEL_VER)
URL_PATCHES_LIST = 'https://access.redhat.com/labs/psb/versions/{}/patches'.format(KERNEL_VER)
REMOTE_URL = 'git@github.com:dshakhray/test_python.git'
asd = 'kernel-rt-3.8.13-rt14.20.el6rt'


def error_handler(fn):
    def wrapper(*args, **kwargs):
        #logger = logging.getLogger(__name__)
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            #logger.error("errrr")
            wrapper(*args, **kwargs)
    return wrapper


@error_handler
def auth():
    if True:
        raise IOError
    driver = webdriver.PhantomJS()
    driver.get("https://www.redhat.com/wapps/sso/login.html")
    time.sleep(3)
    driver.find_element_by_id("username").send_keys("dmalyavkina@cloudlinux.com")
    driver.find_element_by_id("password").send_keys("05Anivis+2592")
    driver.find_element_by_id("_eventId_submit").click()
    time.sleep(3)
    print 'auth'
    return driver


def download_patches():
    driver = auth()
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

    table_id = driver.find_element_by_class_name("table-files")
    rows = table_id.find_elements_by_tag_name("tr")

    for row in rows:
        patch_name = row.find_element_by_class_name("name").text
        if patch_name != '' and patch_name != "Name":
            patches_list.append(patch_name)

    print 'create list of name'
    return patches_list


def create_files(patches_list=None):

    if not os.path.exists(KERNEL_VER):
        os.makedirs(KERNEL_VER)

    patches_list = patches_list or download_patches()
    driver = auth()

    for patch_name in patches_list:
        url = URL_PATCHES % patch_name
        driver.get(url)
        time.sleep(3)
        patch = driver.find_elements_by_tag_name("body")[0].text

        if patch == '':
            driver = auth()
            driver.get(url)
            patch = driver.find_elements_by_tag_name("body")[0].text

        f = open('%s/%s' % (KERNEL_VER, patch_name), 'w')
        f.write(patch.encode('utf-8'))
        f.close()

    print 'create files'


def update_files():
    patches_list = download_patches()
    patches_update = []

    for patch_name in patches_list:
        patch_path = '%s/%s' % (KERNEL_VER, patch_name)
        if not os.path.exists(patch_path):
            patches_update.append(patch_name)
    return patches_update


def git_init():
    repo = git.Repo.init()

    if not repo.remotes:
        origin = repo.create_remote('origin',  url=REMOTE_URL)
    else:
        origin = repo.remotes.origin

    origin.pull('master')
    print 'git_init'


def git_branch():
    repo = git.Repo.init()
    br = repo.create_head(KERNEL_VER)
    repo.head.reference = br
    origin = repo.remotes.origin

    repo.index.add([KERNEL_VER])
    repo.index.commit("Add patches for %s" % KERNEL_VER)
    origin.push(KERNEL_VER)
    print 'git push %s' % KERNEL_VER


def new_kernel():
    git_init()
    create_files()
    #update_files()
    git_branch()


def update_kernel():
    git_init()
    patches_list = update_files()
    create_files(patches_list)
    git_branch()

if __name__ == '__main__':
    #git_init()
    #create_files()
    #update_files()
    #git_push()
    #git_branch()
    auth()