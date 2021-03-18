import requests
import jsonpath

# 防止SSL报错
requests.packages.urllib3.disable_warnings()

# 代理
# proxies={
# 'http':'127.0.0.1:8080',
# 'https':'127.0.0.1:8080'
# }

# 必须改HTTP的头
headers={'content-type': 'application/json'}

url = "https://hackerone.com/graphql"

# 每页的Program数量被限制在25，所以cursor参数需要25*n，然后base64编码
cursor = "MAo="


### 第一个循环请求用来抓取所有的Program
all_programs = []
handle = []
print("-----------------------------------------------------------------")
print("-----------------------------------------------------------------")
print("Start collecting programs")
print("-----------------------------------------------------------------")
print("-----------------------------------------------------------------")
while (type(cursor) == str) :

    all_programs = all_programs + handle
    
    data = '''{"operationName":"DirectoryQuery","variables":{"where":{"_and":[{"_or":[{"offers_bounties":{"_eq":true}},{"external_program":{"offers_rewards":{"_eq":true}}}]},{"_or":[{"submission_state":{"_eq":"open"}},{"submission_state":{"_eq":"api_only"}},{"external_program":{}}]},{"_not":{"external_program":{}}},{"_or":[{"_and":[{"state":{"_neq":"sandboxed"}},{"state":{"_neq":"soft_launched"}}]},{"external_program":{}}]}]},"first":25,"secureOrderBy":{"started_accepting_at":{"_direction":"DESC"}},"cursor":"''' + cursor + '''"},"query":"query DirectoryQuery($cursor: String, $secureOrderBy: FiltersTeamFilterOrder, $where: FiltersTeamFilterInput) {\\n  me {\\n    id\\n    edit_unclaimed_profiles\\n    h1_pentester\\n    __typename\\n  }\\n  teams(first: 25, after: $cursor, secure_order_by: $secureOrderBy, where: $where) {\\n    pageInfo {\\n      endCursor\\n      hasNextPage\\n      __typename\\n    }\\n    edges {\\n      node {\\n        id\\n        bookmarked\\n        ...TeamTableResolvedReports\\n        ...TeamTableAvatarAndTitle\\n        ...TeamTableLaunchDate\\n        ...TeamTableMinimumBounty\\n        ...TeamTableAverageBounty\\n        ...BookmarkTeam\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment TeamTableResolvedReports on Team {\\n  id\\n  resolved_report_count\\n  __typename\\n}\\n\\nfragment TeamTableAvatarAndTitle on Team {\\n  id\\n  profile_picture(size: medium)\\n  name\\n  handle\\n  submission_state\\n  triage_active\\n  publicly_visible_retesting\\n  state\\n  allows_bounty_splitting\\n  external_program {\\n    id\\n    __typename\\n  }\\n  ...TeamLinkWithMiniProfile\\n  __typename\\n}\\n\\nfragment TeamLinkWithMiniProfile on Team {\\n  id\\n  handle\\n  name\\n  __typename\\n}\\n\\nfragment TeamTableLaunchDate on Team {\\n  id\\n  started_accepting_at\\n  __typename\\n}\\n\\nfragment TeamTableMinimumBounty on Team {\\n  id\\n  currency\\n  base_bounty\\n  __typename\\n}\\n\\nfragment TeamTableAverageBounty on Team {\\n  id\\n  currency\\n  average_bounty_lower_amount\\n  average_bounty_upper_amount\\n  __typename\\n}\\n\\nfragment BookmarkTeam on Team {\\n  id\\n  bookmarked\\n  __typename\\n}\\n"}'''
    # r = requests.post(url,data=data,proxies=proxies,headers=headers,verify=False)
    r = requests.post(url,data=data,headers=headers,verify=False)  
    
    endCursor = jsonpath.jsonpath(r.json(),"$..endCursor")
    cursor = endCursor[0]
    handle = jsonpath.jsonpath(r.json(),"$..handle")
    
    print("Programs have been collected: " )
    print(all_programs)
    print("-----------------------------------------------------------------")
    print("-----------------------------------------------------------------")

len_all_programs =  len(all_programs)

print(str(len(all_programs))+ " programs have been Collected")

print("-----------------------------------------------------------------")
print("-----------------------------------------------------------------")

print("Start collecting domains")
print("-----------------------------------------------------------------")
print("-----------------------------------------------------------------")

# with open('all_programs.txt', 'w') as f:
#     for line in all_programs:
#         f.write(line+'\n')
#     f.close


f=open("all_programs.txt","w")
 
for line in all_programs:
    f.write(line+'\n')
f.close()


### 第二个循环请求用来抓取每个Program的Domain
all_targets = []
target_of_single_program = []

for i in range(0,len(all_programs)):

    single_program = all_programs[i]

    

    data = '''{"operationName":"TeamAssets","variables":{"handle":"'''+single_program+'''"},"query":"query TeamAssets($handle: String!) {\\n  me {\\n    id\\n    membership(team_handle: $handle) {\\n      id\\n      permissions\\n      __typename\\n    }\\n    __typename\\n  }\\n  team(handle: $handle) {\\n    id\\n    handle\\n    structured_scope_versions(archived: false) {\\n      max_updated_at\\n      __typename\\n    }\\n    in_scope_assets: structured_scopes(first: 550, archived: false, eligible_for_submission: true) {\\n      edges {\\n        node {\\n          id\\n          asset_type\\n          asset_identifier\\n          rendered_instruction\\n          max_severity\\n          eligible_for_bounty\\n          labels(first: 100) {\\n            edges {\\n              node {\\n                id\\n                name\\n                __typename\\n              }\\n              __typename\\n            }\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    out_scope_assets: structured_scopes(first: 550, archived: false, eligible_for_submission: false) {\\n      edges {\\n        node {\\n          id\\n          asset_type\\n          asset_identifier\\n          rendered_instruction\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'''
    
    # r = requests.post(url,data=data,proxies=proxies,headers=headers,verify=False)
    r = requests.post(url,data=data,headers=headers,verify=False)


    edges_list = r.json()["data"]["team"]["in_scope_assets"]["edges"]
    nodes = {}
    
    for i in range(0, len(edges_list)):

        single_node = r.json()["data"]["team"]["in_scope_assets"]["edges"][i]
        single_asset_type = single_node["node"]["asset_type"]
        single_asset_identifier = single_node["node"]["asset_identifier"]

        # 由于字典不允许有相同的键，所以single_asset_identifier 为键，single_asset_type为值
        nodes[single_asset_identifier] = single_asset_type
        
        

    target_of_single_program = [k for k,v in nodes.items() if v == 'URL']
    all_targets = all_targets + target_of_single_program

    print("Collected  " + str(len(target_of_single_program)) + " In Scope domains of [" + single_program + "] on Hackerone")
    for line in target_of_single_program:
        print(line)
    print("-----------------------------------------------------------------")
    print("-----------------------------------------------------------------")
    


print("Finished")


f=open("all_targets.txt","w")
 
for line in all_targets:
    f.write(line+'\n')
f.close()
