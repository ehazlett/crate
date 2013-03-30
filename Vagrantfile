# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "precise64"
  config.vm.provision :shell, :path => "provision.sh"
  config.vm.hostname = "crate"
  config.vm.network :public_network
  # config.vm.synced_folder "../data", "/vagrant_data"
  #
  config.vm.provider :vmware_fusion do |v|
    v.vmx["memsize"] = "1024"
    v.vmx["displayName"] = "crate"
  end
end
