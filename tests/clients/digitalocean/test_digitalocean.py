import os
import string

import gevent
import pytest
from jumpscale.loader import j
from tests.base_tests import BaseTests


class DigitalOcean(BaseTests):
    def setUp(self):
        self.ssh_client_name = self.random_name()
        self.dg_client_name = self.random_name()
        ssh = j.clients.sshkey.get(name=self.ssh_client_name)

        self.dg = j.clients.digitalocean.get(self.dg_client_name)
        ssh_private_key_path = os.getenv("SSH_PRIVATE_KEY_PATH")
        digital_ocean_access_token = os.getenv("DIGITAL_OCEAN_ACCESS_TOKEN")
        if ssh_private_key_path and digital_ocean_access_token:
            ssh.private_key_path = ssh_private_key_path
            self.dg.token = digital_ocean_access_token
        else:
            raise Exception("Please add (SSH_PRIVATE_KEY_PATH, DIGITAL_OCEAN_ACCESS_TOKEN)  as environment variables ")
        ssh.load_from_file_system()
        self.dg.set_default_sshkey(ssh)
        self.dg_instances = list()

    @pytest.mark.integration
    def test01_test_deploy_project(self):
        """Test for deploying project on Digital Ocean Client.

        **Test Scenario**

        - Get project.
        - Set a random name to be used on Digital Ocean.
        - Wait for project deployment.
        """
        dg_project_client_name = self.random_name()
        project = self.dg.projects.new(dg_project_client_name)
        dg_project_name = self.random_name()
        project.set_digital_ocean_name(dg_project_name)
        self.dg_instances.append(project)
        result = project.deploy(purpose="testing digital ocean client")
        self.assertIsNotNone(result)
        self.wait_instance_deploy(10, self.dg.projects.check_project_exist_remote, dg_project_name)
        self.assertTrue(self.dg.projects.check_project_exist_remote(dg_project_name))

    @pytest.mark.integration
    def test02_test_deploy_droplet(self):
        """Test for deploying droplet on Digital Ocean Client.

        **Test Scenario**

        - Get droplet.
        - Set a random name to be used on Digital Ocean.
        - Wait for droplet deployment.
        """
        dg_droplet_client_name = self.random_name()
        droplet = self.dg.droplets.new(dg_droplet_client_name)
        dg_droplet_name = self.random_name()
        droplet.set_digital_ocean_name(dg_droplet_name)
        self.dg_instances.append(droplet)
        result = droplet.deploy()
        self.assertIsNone(result)
        self.wait_instance_deploy(10, self.dg.droplets.check_droplet_exist_remote, dg_droplet_name)
        self.assertTrue(self.dg.droplets.check_droplet_exist_remote(dg_droplet_name))

    @pytest.mark.integration
    def test03_test_get_project_by_name(self):
        """Test for getting a deployed project on Digital Ocean Client.

        **Test Scenario**

        - Get project.
        - Set a random name to be used on Digital Ocean.
        - Wait for project deployment.
        - Get the deployed project instance.
        """
        dg_project_client_name = self.random_name()
        project = self.dg.projects.new(dg_project_client_name)
        dg_project_name = self.random_name()
        project.set_digital_ocean_name(dg_project_name)
        self.dg_instances.append(project)
        project.deploy(purpose="testing digital ocean client")
        self.wait_instance_deploy(10, self.dg.projects.check_project_exist_remote, dg_project_name)
        self.assertIsNotNone(self.dg.projects.get_project_exist_remote(dg_project_name))

    @pytest.mark.integration
    def test04_test_get_droplet_by_name(self):
        """Test for getting a deployed droplet on Digital Ocean Client.

        **Test Scenario**

        - Get droplet.
        - Set a random name to be used on Digital Ocean.
        - Wait for droplet deployment.
        - Get the deployed droplet instance.
        """
        dg_droplet_client_name = self.random_name()
        droplet = self.dg.droplets.new(dg_droplet_client_name)
        dg_droplet_name = self.random_name()
        droplet.set_digital_ocean_name(dg_droplet_name)
        self.dg_instances.append(droplet)
        droplet.deploy()
        self.wait_instance_deploy(10, self.dg.droplets.check_droplet_exist_remote, dg_droplet_name)
        self.assertIsNotNone(self.dg.droplets.get_droplet_exist_remote(dg_droplet_name))

    @pytest.mark.integration
    def test05_test_get_digital_ocean_images(self):
        """Test for getting digital ocean available images.

        **Test Scenario**

        - Get all the images.
        """
        self.assertIsNotNone(self.dg.images)

    @pytest.mark.integration
    def test06_test_get_digital_ocean_images_names(self):
        """Test for getting digital ocean available image names.

        **Test Scenario**

        - Get all the images names.
        """
        self.assertIsNotNone(self.dg.get_image_names)

    @pytest.mark.integration
    def test07_test_get_digital_ocean_images_names(self):
        """Test for getting digital ocean available images by specific name.

        **Test Scenario**

        - Get all the images by specific name.
        """
        self.assertIsNotNone(self.dg.get_image_names("centos"))

    @pytest.mark.integration
    def test08_test_get_digital_ocean_sizes(self):
        """Test for getting digital ocean available sizes.

        **Test Scenario**

        - Get all the available sizes.
        """
        self.assertIsNotNone(self.dg.sizes)

    @pytest.mark.integration
    def test09_test_get_digital_ocean_regions(self):
        """Test for getting digital ocean available regions.

        **Test Scenario**

        - Get all the available regions.
        """
        self.assertIsNotNone(self.dg.regions)

    @pytest.mark.integration
    def test10_test_get_digital_ocean_region_names(self):
        """Test for getting digital ocean available region names.

        **Test Scenario**

        - Get all the available region names.
        """
        self.assertIsNotNone(self.dg.region_names)

    @pytest.mark.integration
    def test11_test_get_digital_ocean_region(self):
        """Test for getting digital ocean specific region.

        **Test Scenario**

        - Get all the available regions.
        - Get specific region.
        """
        regions = self.dg.region_names
        self.assertIsNotNone(self.dg.get_region(regions[0]))

    @pytest.mark.integration
    def test12_test_get_digital_ocean_ssh_keys(self):
        """Test for getting digital ocean available sshkeys.

        **Test Scenario**

        - Get all the sshkeys.
        """
        self.assertIsNotNone(self.dg.sshkeys)

    @pytest.mark.integration
    def test13_test_get_digital_ocean_get_default_ssh_key(self):
        """Test for getting digital ocean default sshkey.

        **Test Scenario**

        - Get default sshkey.
        """
        self.assertIsNotNone(self.dg.get_default_sshkey())

    @pytest.mark.integration
    def test14_test_get_digital_ocean_get_specific_ssh_key(self):
        """Test for getting digital ocean specific sshkey.

        **Test Scenario**

        - Get all the available sshkeys .
        - Get specific sshkey by name.
        """
        ssh_keys = self.dg.sshkeys
        self.assertIsNotNone(self.dg.get_sshkey(ssh_keys[0].name))

    def wait_instance_deploy(self, seconds, check_exist_method, name):
        for _ in range(seconds):
            if check_exist_method(name):
                return True
            gevent.sleep(1)
        return False

    def tearDown(self):
        for item in self.dg_instances:
            item.delete_remote()
        j.clients.sshkey.delete(name=self.ssh_client_name)
        j.clients.digitalocean.delete(self.dg_client_name)
