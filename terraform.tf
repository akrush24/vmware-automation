variable "vmname" { default = "test-vm"}
variable "ipvm" { default = ""}

provider "vsphere" {
  user           = ""
  password       = ""
  vsphere_server = "vc-linx.srv.local"
  allow_unverified_ssl = true
}


data "vsphere_datacenter" "dc" {
  name = "Datacenter-Linx"
}

data "vsphere_datastore" "datastore" {
  name          = "27_localstore_r10"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_compute_cluster" "cluster" {
  name          = "linx-cluster01"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_network" "network" {
  name          = "192.168.222"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_virtual_machine" "template" {
  #name          = "ubuntu-16.04"
  name          = "template_centos7.3"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

resource "vsphere_virtual_machine" "vm" {
  name             = "${var.vmname}"
  resource_pool_id = "${data.vsphere_compute_cluster.cluster.resource_pool_id}"
  datastore_id     = "${data.vsphere_datastore.datastore.id}"

  num_cpus = 2
  memory   = 4096
  guest_id = "${data.vsphere_virtual_machine.template.guest_id}"

  scsi_type = "${data.vsphere_virtual_machine.template.scsi_type}"

  network_interface {
    network_id   = "${data.vsphere_network.network.id}"
    adapter_type = "${data.vsphere_virtual_machine.template.network_interface_types[0]}"
  }

  disk {
    label            = "disk0"
    size             = 100
# "${data.vsphere_virtual_machine.template.disks.0.size}"
    eagerly_scrub    = "${data.vsphere_virtual_machine.template.disks.0.eagerly_scrub}"
    thin_provisioned = "${data.vsphere_virtual_machine.template.disks.0.thin_provisioned}"
  }

  clone {
    template_uuid = "${data.vsphere_virtual_machine.template.id}"

    customize {
      linux_options {
        host_name = "${var.vmname}"
        domain    = "srv.local"
      }

      network_interface {
        ipv4_address = "${var.ipvm}"
        ipv4_netmask = 24
      }

      ipv4_gateway = "192.168.222.1"
    }
  }


}
