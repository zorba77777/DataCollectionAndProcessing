import requests
import time
from threading import Thread
from lesson8.my_data import MyVkData

# OAuth access tokens for Vkontakte API
token = MyVkData.get_token()

# Vkontakte API limitations
f_1_max = 300  # Maximum users per request
f_2_max = 24  # 25 is maximum amount of methods which are used in one 'execute' method
t = 0.35  # 3 is maximum requests per one second
max_edges_3 = 1500  # Limitation because of a lot amount of received data


# Defining GET-request for API
def vk(method, parameters, token):
    return requests.get(
        'https://api.vk.com/method/%s?%s&access_token=%s' % (method, '&'.join(parameters), token)).json()


# Main method
def vk_mutual(user_1, user_2):
    # Checking input data
    try:
        user_1 = int(user_1)
        user_2 = int(user_2)
    except:
        users_info = vk('users.get', ['user_ids=%s,%s' % (user_1, user_2), 'v=5.4'], token)['response']
        time.sleep(t)
        try:
            user_1 = int(users_info[0]['id'])
            user_2 = int(users_info[1]['id'])
        except:
            return 'User id parameter error'

    edges_1, edges_2, edges_3 = set(), set(), set()

    # This filters are using for filtering unnecessary connections between 'user_1' and 'user_2'
    filter_1, filter_2 = set(), set()
    filter_1.update([user_1, user_2])

    # Getting friends of 'user_1'
    try:
        friends_1 = set(
            vk('friends.get', ['user_id=%s' % user_1, 'order=hints', 'count=900', 'v=5.4'], token)['response']['items'])
        time.sleep(t)
    except:
        return "User's account is private"

    # Getting mutual friends between 'user_1' and 'user_2'. Saving results to 'edges_1'
    response_mutual = vk('friends.getMutual',
                         ['source_uid=%s' % user_1, 'order=hints', 'target_uid=%s' % user_2, 'v=5.4'],
                         token)
    if 'response' in response_mutual:
        mutual_friends = response_mutual['response']
        time.sleep(t)
        for user in mutual_friends:
            edges_1.update([(user_1, user), (user, user_2)])
            friends_1.remove(user)
            filter_1.update([user])

    # Getting mutual friends between 'user_2' and friends of 'user_1'. Saving results to 'edges_2'
    user_1_mutual_friends, temp_users, j = [], [], 0

    for i, friend in enumerate(friends_1):
        temp_users += [friend]
        j += 1
        if j == f_1_max:
            response_mutual = vk('friends.getMutual', ['source_uid=%s' % user_2, 'order=hints',
                                                       'target_uids=%s' % str(temp_users)[1:-1], 'v=5.4'], token)
            if 'response' in response_mutual:
                user_1_mutual_friends += response_mutual['response']
                temp_users, j = [], 0
                time.sleep(t)

        if i == len(friends_1) - 1 and len(friends_1) % f_1_max != 0:
            response_mutual = vk('friends.getMutual', ['source_uid=%s' % user_2, 'order=hints',
                                                       'target_uids=%s' % str(temp_users)[1:-1], 'v=5.4'], token)
            if 'response' in response_mutual:
                user_1_mutual_friends += response_mutual['response']
                time.sleep(t)

    for friend in user_1_mutual_friends:
        if friend['id'] != user_2 and friend['id'] not in filter_1:
            try:
                if friend['common_count'] > 0:
                    for common_friend in friend['common_friends']:
                        if common_friend != user_1 and common_friend not in filter_1:
                            edges_2.update(
                                [(user_1, friend['id']), (friend['id'], common_friend), (common_friend, user_2)])
                            friends_1.remove(friend['id'])
                            filter_2.update([friend['id'], common_friend])
            except:
                continue

    # Getting mutual friends between friends of 'user_2' and friends of 'user_1'. Saving results to 'edges_3'
    filter_3 = filter_1.union(filter_2)
    friends_1 = list(friends_1)

    def get_edges_3(friends_1, token):

        # 'prefix_code' is a part of string that is generating for 'execute' request
        prefix_code = 'code=var friends = API.friends.get({"v": "5.4", "user_id":"%s", "count":"500", "order": ' \
                      '"hints"}).items; ' % user_2
        lines, j, k = [], 0, -1
        for i, friend in enumerate(friends_1):
            lines += [
                'API.friends.getMutual({"v": "5.4", "source_uid": "%s", "count":"500", "target_uids": friends})' % friend]  # Generating string for 'execute' request.
            j += 1
            if j == f_2_max:
                code = prefix_code + 'return [' + ','.join(str(x) for x in lines) + '];'
                response = vk('execute', [code, 'v=5.4'], token)
                for friends in response['response']:
                    k += 1
                    if len(edges_3) < max_edges_3:
                        try:
                            for one_friend in friends:
                                if one_friend['common_count'] > 0:
                                    for common_friend in one_friend['common_friends']:
                                        if common_friend not in filter_3 and one_friend['id'] not in filter_3:
                                            edges_3.update([(user_1, friends_1[k]), (friends_1[k], common_friend),
                                                            (common_friend, one_friend['id']),
                                                            (one_friend['id'], user_2)])
                        except:
                            continue
                lines, j = [], 0
                time.sleep(t)

            if i == len(friends_1) - 1 and len(friends_1) % f_2_max != 0:
                code = prefix_code + 'return [' + ','.join(str(x) for x in lines) + '];'
                response = vk('execute', [code, 'v=5.4'], token)
                for friends in response['response']:
                    k += 1
                    if len(edges_3) < max_edges_3:
                        try:
                            for one_friend in friends:
                                if one_friend['common_count'] > 0:
                                    for common_friend in one_friend['common_friends']:
                                        if common_friend not in filter_3 and one_friend['id'] not in filter_3:
                                            edges_3.update([(user_1, friends_1[k]), (friends_1[k], common_friend),
                                                            (common_friend, one_friend['id']),
                                                            (one_friend['id'], user_2)])
                        except:
                            continue
                time.sleep(t)

    t1 = Thread(target=get_edges_3, args=(friends_1[: int(len(friends_1) * 1 / 5)], token))
    t2 = Thread(target=get_edges_3, args=(friends_1[int(len(friends_1) * 1 / 5): int(len(friends_1) * 2 / 5)], token))
    t3 = Thread(target=get_edges_3, args=(friends_1[int(len(friends_1) * 2 / 5): int(len(friends_1) * 3 / 5)], token))
    t4 = Thread(target=get_edges_3, args=(friends_1[int(len(friends_1) * 3 / 5): int(len(friends_1) * 4 / 5)], token))
    t5 = Thread(target=get_edges_3, args=(friends_1[int(len(friends_1) * 4 / 5):], token))

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()

    # Getting info about users
    edges = list(edges_1) + list(edges_2) + list(edges_3)
    nodes = []
    for edge in edges:
        nodes += [edge[0], edge[1]]
    nodes = list(set(nodes))
    nodes_info, temp_nodes, j = [], [], 0

    for i, node in enumerate(nodes):
        temp_nodes += [node]
        j += 1
        if j == f_1_max:
            nodes_info += \
                vk('users.get', ['user_ids=%s' % str(temp_nodes)[1:-1], 'fields=first_name, last_name', 'v=5.4'],
                   token)[
                    'response']
            temp_nodes, j = [], 0
            time.sleep(t)
        if i == len(nodes) - 1 and len(nodes) % f_1_max != 0:
            response_user = vk('users.get', ['user_ids=%s' % str(temp_nodes)[1:-1], 'fields=first_name, last_name', 'v=5.4'],
                   token)
            if 'response' in response_user:
                nodes_info += response_user['response']
                time.sleep(t)

    for i, node in enumerate(nodes_info):
        try:
            nodes[i] = (nodes[i], {'first_name': node['first_name'], 'last_name': node['last_name']})
        except:
            continue

    # 'param' is a parameter for visualisation
    param = len(edges_1) + len(edges_2)

    return [user_1, user_2, nodes_info, edges, param]
