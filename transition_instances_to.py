#!/usr/bin/env python
from boto.ec2.connection import EC2Connection
import argparse
import os

class InstanceManager(object):

    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.connection = EC2Connection(aws_access_key_id, aws_secret_access_key)


    def start_boxes_named(self, name):
        boxes = self.connection.get_only_instances(filters={"tag:Name" : name})
        for box in boxes:
            if box.state != "running":
                box.start()

        while self.are_all_boxes_in_state(boxes, "running") == False:
            pass

    def stop_boxes_named(self, name):
        boxes = self.connection.get_only_instances(filters={"tag:Name" : name})
        for box in boxes:
            if box.state == "running":
                box.stop()

        while self.are_all_boxes_in_state(boxes, "stopped") == False:
            pass

    def dns_for_boxes_named(self, name):
        return [box.dns_name for box in self.connection.get_only_instances(filters={"tag:Name" : name})]

    def are_all_boxes_in_state(self, boxes, state):
        box_ids = [box.id for box in boxes]
        return_val = reduce(lambda x, y: x and y, map(lambda x: x.state == state, self.connection.get_only_instances(instance_ids=box_ids)))
        return return_val

       
def command_line_controller():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(dest="action" , help="Action to be performed on instances (start, stop, etc).")
    parser.add_argument(dest="instance_name" , help="Instance name (key name) to wait for to start.")
    arguments = parser.parse_args()
    aws_secret_access_key = os.getenv("AWS_SECRET_KEY")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")

    manager = InstanceManager(aws_access_key_id, aws_secret_access_key)
    return_val = None
    if arguments.action == "start":
        print "Starting boxes named %s." % arguments.instance_name
        manager.start_boxes_named(arguments.instance_name)
        return_val = manager.dns_for_boxes_named(arguments.instance_name)
    elif arguments.action == "stop":
        print "Stopping boxes named %s." % arguments.instance_name
        manager.stop_boxes_named(arguments.instance_name)


    print return_val

    return return_val


if __name__ == "__main__":
    command_line_controller()
