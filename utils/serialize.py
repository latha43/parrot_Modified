import yaml

def serialize():
     with open("rtmbot.conf", "r") as file:
        dic = yaml.load(file)
        for item in dic.iteritems():
            if "HOST" in item:
                rq_host = item[1]
            if "PORT" in item:
                rq_port = item[1]
            if "MAPPER_FILE" in item:
                mapper_file = item[1]
            if "METHOD_MAPPER" in item:
                item[1][0] = {x: mapper_file for x in item[1][0]}
                method_mapper = item[1][0]
            if "PLAYBOOK_MAPPER" in item:
                playbook_mapper = item[1][0]
        return [rq_host,rq_port,method_mapper,playbook_mapper]