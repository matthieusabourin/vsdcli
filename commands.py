# -*- coding: utf-8 -*-

import os
import logging

from bambou.exceptions import BambouHTTPError
from vsdk import NUVSDSession
from vsdk.utils import set_log_level
from printer import Printer
from utils import Utils, VSDKInspector


class VSPCommand(object):
    """ VSD CLI commands

    """
    @classmethod
    def execute(cls, args):
        """ Execute CLI command """

        func = getattr(cls, args.command)
        cls._check_arguments(args)
        cls._define_verbosity(args.verbose)
        func(args)

    ### Commands

    @classmethod
    def list(cls, args):
        """ List all objects

        """
        inspector = VSDKInspector(args.version)
        name = Utils.get_singular_name(args.name)
        instance = inspector.get_vsdk_instance(name)
        session = cls._get_user_session(args)
        parent = inspector.get_vsdk_parent(args.parent_infos, session.user)

        classname = instance.__class__.__name__[2:]
        plural_classname = Utils.get_plural_name(classname)
        fetcher_name = Utils.get_python_name(plural_classname)

        try:
            fetcher = getattr(parent, fetcher_name)
        except:
            Printer.raise_error('%s failed to found fetcher %s' % (parent.rest_name, instance.fetcher_name))

        (fetcher, parent, objects, connection) = fetcher.fetch(filter=args.filter)

        if objects is None:
            Printer.raise_error('Could not retrieve. Activate verbose mode for more information')

        Printer.success('%s %s have been retrieved' % (len(objects), instance.rest_resource_name))
        Printer.output(objects, fields=args.fields, json=args.json)

    @classmethod
    def show(cls, args):
        """ Show object details

            Args:
                uuid: Identifier of the object to show
        """
        inspector = VSDKInspector(args.version)
        name = Utils.get_singular_name(args.name)
        instance = inspector.get_vsdk_instance(name)
        instance.id = args.id
        cls._get_user_session(args)

        try:
            (instance, connection) = instance.fetch()
        except Exception, e:
            Printer.raise_error('Could not find %s with id `%s`. Activate verbose mode for more information:\n%s' % (name, args.id, e))

        Printer.success('%s with id %s has been retrieved' % (name, args.id))
        Printer.output(instance, fields=args.fields, json=args.json, headers={'Attribute', 'Value'})

    @classmethod
    def create(cls, args):
        """ Create an object

        """
        inspector = VSDKInspector(args.version)
        name = Utils.get_singular_name(args.name)
        instance = inspector.get_vsdk_instance(name)
        session = cls._get_user_session(args)
        parent = inspector.get_vsdk_parent(args.parent_infos, session.user)
        attributes = cls._get_attributes(args.params)

        cls._fill_instance_with_attributes(instance, attributes)

        try:
            (instance, connection) = parent.create_child(instance)
        except Exception, e:
            Printer.raise_error('Cannot create %s:\n%s' % (name, e))

        Printer.success('%s has been created with ID=%s' % (name, instance.id))
        Printer.output(instance, json=args.json)

    @classmethod
    def update(cls, args):
        """ Update an existing object


        """
        inspector = VSDKInspector(args.version)
        name = Utils.get_singular_name(args.name)
        instance = inspector.get_vsdk_instance(name)
        instance.id = args.id
        attributes = cls._get_attributes(args.params)

        cls._get_user_session(args)

        try:
            (instance, connection) = instance.fetch()
        except Exception, e:
            Printer.raise_error('Could not find %s with id `%s`. Activate verbose mode for more information:\n%s' % (name, args.id, e))

        cls._fill_instance_with_attributes(instance, attributes)

        try:
            (instance, connection) = instance.save()
        except Exception, e:
            Printer.raise_error('Cannot update %s:\n%s' % (name, e))

        Printer.success('%s with ID=%s has been updated' % (name, instance.id))
        Printer.output(instance, json=args.json)

    @classmethod
    def delete(cls, args):
        """ Delete an existing object


        """
        inspector = VSDKInspector(args.version)
        name = Utils.get_singular_name(args.name)
        instance = inspector.get_vsdk_instance(name)
        instance.id = args.id

        cls._get_user_session(args)

        try:
            (instance, connection) = instance.delete()
        except Exception, e:
            Printer.raise_error('Could not delete %s with id `%s`. Activate verbose mode for more information:\n%s' % (name, args.id, e))

        Printer.success('%s with ID=%s has been deleted' % (name, instance.id))

    @classmethod
    def objects(cls, args):
        """ List all objects of the VSD

        """
        inspector = VSDKInspector(args.version)
        objects = []

        if args.parent:
            name = Utils.get_singular_name(args.parent)
            instance = inspector.get_vsdk_instance(name)

            objects = [Utils.get_plural_name(name) for name in instance.children_rest_names]
        else:
            objects = inspector.get_all_objects()

        if args.child:
            child = Utils.get_singular_name(args.child)
            parents = []
            for name in objects:
                singular_name = Utils.get_singular_name(name)
                instance = inspector.get_vsdk_instance(singular_name)

                if child in instance.children_rest_names:
                    parents.append(name)

            objects = parents

        if args.filter:
            objects = [name for name in objects if args.filter in name]

        objects.sort()

        Printer.success('%s objects found.' % len(objects))
        Printer.output(objects, json=args.json, headers={'Name'})

    ### General methods

    @classmethod
    def _check_arguments(cls, args):
        """ Check arguments and environment variables

        """

        args.username = args.username if args.username else os.environ.get('VSDCLI_USERNAME', None)
        args.password = args.password if args.password else os.environ.get('VSDCLI_PASSWORD', None)
        args.api = args.api if args.api else os.environ.get('VSDCLI_API_URL', None)
        args.version = args.version if args.version else os.environ.get('VSDCLI_API_VERSION', None)
        args.enterprise = args.enterprise if args.enterprise else os.environ.get('VSDCLI_ENTERPRISE', None)
        args.json = True if os.environ.get('VSDCLI_JSON_OUTPUT') == 'True' else args.json

        if args.username is None or len(args.username) == 0:
            Printer.raise_error('Please provide a username using option --username or VSDCLI_USERNAME environment variable')

        if args.password is None or len(args.password) == 0:
            Printer.raise_error('Please provide a password using option --password or VSDCLI_PASSWORD environment variable')

        if args.api is None or len(args.api) == 0:
            Printer.raise_error('Please provide an API URL using option --api or VSDCLI_API_URL environment variable')

        if args.enterprise is None or len(args.enterprise) == 0:
            Printer.raise_error('Please provide an enterprise using option --enterprise or VSDCLI_ENTERPRISE environment variable')

        setattr(args, "name", getattr(args, args.command, None))
        del(args.command)

    @classmethod
    def _get_user_session(cls, args):
        """ Get api key

            Args:
                username: username to get an api key
                password: password to get an api key
                api: URL of the API endpoint
                enterprise: Name of the enterprise to connect

            Returns:
                Returns an API Key if everything works fine
        """
        session = NUVSDSession(username=args.username, password=args.password, enterprise=args.enterprise, api_url=args.api, version=args.version)
        try:
            session.start()
        except BambouHTTPError as error:
            if error.response.status_code == 401:
                Printer.raise_error('Could not log in to the VSD %s (API %s) with username=%s password=%s enterprise=%s' % (args.api, args.version, args.username, args.password, args.enterprise))
            else:
                Printer.raise_error('Cannot access VSD %s. Current vsdk version (%s) tried to connect to the VSD API %s' % (args.api, VSDKInspector.get_installed_version(), args.version))

        user = session.user

        if user.api_key is None:
            Printer.raise_error('Could not get a valid API key. Activate verbose mode for more information')

        return session

    @classmethod
    def _define_verbosity(cls, verbose):
        """ Defines verbosity

            Args:
                verbose: Boolean to activate or deactivate DEBUG mode

        """
        if verbose:
            Printer.info('Verbose mode is now activated.')
            set_log_level(logging.DEBUG)
        else:
            set_log_level(logging.ERROR)

    @classmethod
    def _get_attributes(cls, params):
        """ Transforms a list of Key=Value
            to a dictionary of attributes

            Args:
                params: list of Key=Value

            Returns:
                A dict

        """
        attributes = dict()

        for param in params:
            infos = param.split('=', 1)

            if len(infos) != 2:
                Printer.raise_error('Parameter %s is not in key=value format' % param)

            attribute_name = Utils.get_python_name(infos[0])
            attributes[attribute_name] = infos[1]

        return attributes

    @classmethod
    def _fill_instance_with_attributes(cls, instance, attributes):
        """ Fill the given instance with attributes

            Args:
                instance: the instance to fill
                attributes: the dictionary of attributes

            Returns:
                The instance filled or throw an exception

        """
        for attribute_name, attribute_value in attributes.iteritems():

            attribute = instance.get_attribute_infos(attribute_name)
            if attribute is None:
                Printer.raise_error('Attribute %s could not be found in %s' % (attribute_name, instance.rest_name))

            try:
                value = attribute.attribute_type(attribute_value)
                setattr(instance, attribute_name, value)
            except Exception, e:
                Printer.raise_error('Attribute %s could not be set with value %s\n%s' % (attribute_name, attribute_value, e))

        # TODO-CS: Remove validation when we will have all attribute information from Swagger...
        # if not instance.validate():
        #     Printer.raise_error('Cannot validate %s for creation due to following errors\n%s' % (instance.rest_name, instance.errors))
