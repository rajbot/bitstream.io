Title:  Using Logspout and Papertrail to collect logs from containers running in Amazon ECS
Author: raj
Tags:   logspout, aws, ecs, docker, papertrail
Date:   2016-03-01


Amazon [ECS](https://aws.amazon.com/ecs/) is a container management service that makes it
easy to deploy Docker containers on AWS. However, once you scale to many containers running
on many EC2 nodes, you will need a centralized service to collect and analyze docker logs.

Centralized log collection is quite easy to set up with the [Logspout](https://github.com/gliderlabs/logspout)
Docker container and the [Papertrail](https://papertrailapp.com) log management service.

Logspout is a docker container that attaches to all the other docker containers running
on a host and forwards the docker logs somewhere.

Papertrail is a log aggregator that provides a remote syslog endpoint. It has a nice
web console and a fast search engine that lets you tail logs in realtime and
filter by syslog priority, machine name, program name, or search string.
Papertrail also has integrations for sending alerts to many services, such as PagerDuty,
Amazon SNS, and Slack.

Log aggregation for ECS is easily achieved by running one Logspout container on
each EC2 node in your ECS cluster, which will forward logs for all docker containers
running on the EC2 node to Papertrail using syslog. This lets us see and analyze
logs in a centralized place, but also leaves the logs on the EC2 nodes in case
something goes wrong with log forwarding and we need to analyze the logs
directly on the host.

We can deploy Logspout in ECS using the standard ECS scheduler, but by default, we can't
tell ECS to schedule exactly one Logspout container per EC2 node. However, if we launch
the same number of Logspout containers as EC2 nodes in the cluster, and we tell ECS to
attach an unused port to Logspout, then the scheduler will launch exactly one Logspout
container per EC2 node.

You can use the `boto` python library with the code below to create a Task Definition and
an ECS Service for Logspout in your ECS cluster:

```python

# Create ECS Task Definition

task_def = {
    'image': 'gliderlabs/logspout',
    'name': 'logspout',
    'essential': True,
    'memory': 128,
    'cpu': 1,
    'portMappings': [{
        'containerPort': 1234,   # trick ECS into only scheduling one container per node
        'hostPort': 1234,        # by mapping a dummy port to our logspout container
        'protocol': 'tcp'
    }],
    'mountPoints': [{
        'containerPath': '/tmp/docker.sock',    # logspout uses the docker unix socket
        'sourceVolume': 'dockersock'            # to gather logs from the other containers
    }],
    'command': ["syslog://HOST.papertrailapp.com:PORT"]     #replace HOST and PORT with your account's config
}

volume = {
    'host': {'sourcePath': '/var/run/docker.sock'},
    'name': 'dockersock'
}

client = boto3.client('ecs', region_name='xxx')

client.register_task_definition(
    family = 'my-task-def',
    containerDefinitions = [task_def],
    volumes = [volume]
)


# Create ECS Service

client.create_service(
    desiredCount = N, #replace with number of EC2 nodes in your cluster
    cluster = 'my-cluster-name',
    serviceName = 'logspout-service',
    taskDefinition = 'my-task-def'
)
```

After ECS launches the logspout containers, your docker logs will start appearing in Papertrail.
