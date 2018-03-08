import yaml

with open("rtmbot.conf") as stream:
    dict = yaml.load(stream)
    for item in dict.iteritems():
        if "RQ_HOST" in item:
            rq_host = item[1]
        if "RQ_PORT" in item:
            rq_port = item[1]
        if "MAPPER_FILE" in item:
            mapper_file = item[1]
        if "METHOD_MAPPER" in item:
            item[1][0] = {key: mapper_file for key in item[1][0]}
            method_mapper_value = item[1][0]
        if "PLAYBOOK_MAPPER" in item:
            playbook_mapper_value = item[1][0]
