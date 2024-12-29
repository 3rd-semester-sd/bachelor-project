variable "cluster_name" {
  type        = string
  description = "The name of the AKS cluster"
}

variable "rg_name" {
  type        = string
  description = "The name of the resource group"
}

variable "rg_location" {
  type        = string
  description = "The location of the resource group"
}

variable "dns_prefix" {
  type        = string
  description = "The DNS prefix for the AKS cluster"
}

variable "dnp_name" {
  type        = string
  description = "The name of the default node pool"
}

variable "dnp_node_count" {
  type        = number
  description = "The number of nodes in the default node pool"
}

variable "dnp_vm_size" {
  type        = string
  description = "The size of the VMs in the default node pool"
}
