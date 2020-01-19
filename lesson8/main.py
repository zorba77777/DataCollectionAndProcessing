from lesson8.vk_mutual import vk_mutual

if __name__ == '__main__':
    first_url = 'https://vk.com/id296612364'
    second_url = 'https://vk.com/sergei.simonyan'

    returned_value = vk_mutual(first_url.split('/')[3], second_url.split('/')[3])

    if (type(returned_value) is list) & (len(returned_value[3])):
        linked_ids = returned_value[3]

        links = set()
        for ids in linked_ids:
            for id in ids:
                links.add('https://vk.com/id' + str(id))

        db_record = {
            "person_a": first_url,  # ссылка на персону A
            "person_b": second_url,  # ссылка на персону B
            "chain": list(links)  # цепочка (список) из ссылок
        }









