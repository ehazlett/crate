# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "quantal64"
  config.vm.provision :shell, :path => "vagrant_provision.sh"
  config.vm.hostname = "crate"
  config.vm.network :public_network
  config.vm.provider :vmware_fusion do |v|
    v.vmx["numvcpus"] = "4"
    v.vmx["memsize"] = "2048"
    v.vmx["displayName"] = "crate"
  end
end
