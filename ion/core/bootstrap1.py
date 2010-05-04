#!/usr/bin/env python

"""
@file ion/core/bootstrap.py
@author Michael Meisinger
@brief main module for bootstrapping the system
"""

import logging
from twisted.internet import defer
import time

from magnet.spawnable import Receiver
from magnet.spawnable import send
from magnet.spawnable import spawn
from magnet.container import Container
from magnet.store import Store

from ion.core import ioninit
from ion.core.supervisor import Supervisor, ChildProcess
from ion.core.base_process import procRegistry
from ion.util.config import Config
import ion.util.procutils as pu

CONF = ioninit.config(__name__)

# Static definition of message queues
ion_messaging = Config(CONF.getValue('messaging_cfg')).getObject()

# Static definition of service names
ion_services = Config(CONF.getValue('services_cfg')).getObject()

# Local process ids
process_ids = procRegistry
# TODO: create nameRegsitry in Cassandra
nameRegistry = Store()


@defer.inlineCallbacks
def start():
    """Main function of bootstrap. Starts system with static config
    """
    yield _bootstrap(ion_messaging,ion_services)

@defer.inlineCallbacks
def _bootstrap(queues, procs):
    """Bootstraps the system from a configuration 
    """
    logging.info("ION SYSTEM bootstrapping now...")
    yield bs_messaging(queues)
    yield bs_processes(procs)
    
@defer.inlineCallbacks
def bs_messaging(messagingCfg):
    """Bootstraps the messaging resources 
    """
    # for each messaging resource call Magnet to define a resource
    for name, msgResource in messagingCfg.iteritems():
        scope = msgResource.get('args',{}).get('scope','global')
        msgName = name
        if scope == 'local':
            msgName = Container.id + "." + msgName
        if scope == 'group':
            msgName = CONF['container_group'] + "." + msgName

        # declare queues, bindings as needed
        logging.info("Msg name config: name="+msgName+', '+str(msgResource))
        yield Container.configure_messaging(msgName, msgResource)
        
        # save name is the name registry
        yield nameRegistry.put(msgName, msgResource)
        
@defer.inlineCallbacks
def bs_processes(procs):
    """Bootstraps a set of processes 
    """
    sup = bs_prepSupervisor(procs)

    logging.info("Spawning bootstrap supervisor")
    supId = yield spawn(sup.receiver)
    yield process_ids.put("bootstrap", supId)

    yield sup.spawnChildProcesses()
    for child in sup.childProcesses:
        procId = child.procId
        yield process_ids.put(child.procName, procId)

    logging.debug("process_ids: "+ str(process_ids.kvs))

    yield sup.initChildProcesses()

def bs_prepSupervisor(procs):
    """Prepares a Supervisor class instance with configured child processes.
    """
    logging.info("Preparing bootstrap supervisor")
   
    children = []
    for procName, procDef in procs.iteritems():
        child = ChildProcess(procDef['module'], procDef['class'], None)
        child.procName = procName
        children.append(child)

    logging.debug("Supervisor child procs: "+str(children))

    sup = Supervisor()
    sup.childProcesses = children
    return sup

"""
from ion.core import bootstrap as b
b.start()
"""