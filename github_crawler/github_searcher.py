#-*- coding: utf-8 -*-

import httplib2
import json
import base64
import csv
import re
from time import sleep

class incompleteError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class NoresultError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

# 언어별 1000번째 저장소 star수
lang_thousand={
    'ActionScript':10,
    'C':428,
    'CSharp':227,
    'CPP':421,
    'Clojure':64,
    'CoffeeScript':63,
    'CSS':262,
    'Go':475,
    'Haskell':35,
    'HTML':322,
    'Java':1270,
    'Javascript':2908,
    'Lua':36,
    'Matlab':9,
    'Objective-C':716,
    'Perl':32,
    'PHP':458,
    'Python':1012,
    'R':30,
    'Ruby':600,
    'Scala':75,
    'Shell':215,
    'Swift':359,
    'TeX':15,
    'Vim-script':59
}

field_list=[
    'id','name','full_name',
    'owner','private','html_url',
    'description','fork','url',
    'forks_url','keys_url','keys_url',
    'collaborators_url','teams_url','hooks_url',
    'issue_events_url','events_url','assignees_url',
    'branches_url','tags_url','blobs_url',
    'git_tags_url','git_refs_url','trees_url',
    'statuses_url','languages_url','stargazers_url',
    'contributors_url','subscribers_url','subscription_url',
    'commits_url','git_commits_url','comments_url',
    'issue_comment_url','contents_url','compare_url',
    'merges_url','archive_url','downloads_url',
    'issues_url','pulls_url','milestones_url',
    'notifications_url','labels_url','releases_url',
    'deployments_url','created_at','updated_at',
    'pushed_at','git_url','ssh_url',
    'clone_url','svn_url','homepage',
    'size','stargazers_count','watchers_count',
    'language','has_issues','has_projects',
    'has_downloads','has_wiki','has_pages',
    'forks_count','mirror_url','open_issues_count',
    'forks','open_issues','watchers',
    'default_branch','permissions','score'
]

def Request(url):
    http = httplib2.Http()
    auth = base64.encodestring('rlrlaa123' + ':' + 'ehehdd009')
    return http.request(url,'GET',headers={ 'Authorization' : 'Basic ' + auth})

def WriteCSV(json_parsed,field_name):
    with open('data/Top_repositories(final).csv','a') as csvfile:
        fieldnames = []
        fieldnames_dict = {}
        for field in field_name:
            fieldnames.append(field)
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        for data in json_parsed:
            for field in field_name:
                fieldnames_dict[field]=data[field]
            try:
                writer.writerow(fieldnames_dict)
                fieldnames_dict = {}
            except UnicodeEncodeError as e1:
                with open('data/error_Top_repositories(final).csv','a') as csvfile:
                    fieldnames_dict['description']=fieldnames_dict['description'].encode('utf-8')
                    try:
                        writer.writerow(fieldnames_dict)
                        fieldnames_dict = {}
                    except UnicodeEncodeError as e2:
                        errorwriter = csv.writer(csvfile)
                        errorwriter.writerow([fieldnames_dict['full_name'],e2])
                        writer.writerow({})
                        fieldnames_dict = {}


def FindLink(response,which):
    if which == 'next':
        return re.compile('([0-9]+)>; rel="next"').findall(response['link'])
    elif which == 'last':
        return re.compile('([0-9]+)>; rel="last"').findall(response['link'])

def NextPage(url,next,last):
    count_last = 2
    while count_last<int(last[0])+1:
        try:
            next_url = url + '&page=' + str(next[0])
            print next_url
            response, content = Request(next_url)
            if json.loads(content)['incomplete_results'] == False:
                json_parsed = json.loads(content)['items']
                WriteCSV(json_parsed,field_list)
                next = FindLink(response,'next')
                count_last += 1
            else:
                raise incompleteError('Not incomplete results, try again')
        except incompleteError as e:
            print e
        except KeyError as e:
            print e
            print 'what happened'
            sleep(2)

lang_key = lang_thousand.keys()
# First top 1000 stars respositories per language
for lang in lang_key:
    while True:
        url = 'https://api.github.com/search/repositories?q=stars:>5+language:"'+lang+'"&per_page=100&sort=stars'
        print url
        try:
            response, content = Request(url)
            if json.loads(content)['incomplete_results']==False:
                print 'Respository count: '+str(json.loads(content)['total_count'])
                json_parsed = json.loads(content)['items']
                WriteCSV(json_parsed,field_list)
                try:
                    next = FindLink(response,'next')
                    NextPage(url,next,[10])
                    break
                except KeyError as e:
                    print e
            else:
                raise incompleteError('Not incomplete results, try again')
        except KeyError as e:
            print e
            sleep(2)

# From 1001 top repository ~ 135252 top repository
lang_value = lang_thousand.items()
for lang in lang_value:
    # 1001번째 star 수 부터 카운트
    count=lang[1]-1
    while count>49:
        url = 'https://api.github.com/search/repositories?q=stars:'+str(count)+'+language:"'+lang[0]+'"&per_page=100&sort=stars'
        print url
        try:
            response, content = Request(url)
            if json.loads(content)['incomplete_results'] == False:
                print 'Repository count: '+str(json.loads(content)['total_count'])
                json_parsed = json.loads(content)['items']
                WriteCSV(json_parsed,field_list)
                try:
                    next = FindLink(response,'next')
                    last = FindLink(response,'last')
                    NextPage(url,next,last)
                except KeyError as e:
                    print e
            else:
                print 'incomplete result'
            count -= 1
        except KeyError as e:
            print e
            sleep(2)