resource "azurerm_postgresql_server" "primary" {
  name                = var.primary_server_name
  resource_group_name = var.rg_name
  location            = var.rg_location

  sku_name = var.sku_name

  storage_mb                   = 5120
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  administrator_login          = var.admin_login
  administrator_login_password = var.admin_password
  version                      = "9.5"
  ssl_enforcement_enabled      = true
}

resource "azurerm_postgresql_server" "replica" {
  depends_on = [azurerm_postgresql_server.primary]

  count = var.create_replica ? 1 : 0

  name                = "${var.primary_server_name}-replica-1"
  resource_group_name = var.rg_name
  location            = var.rg_location

  sku_name = var.sku_name

  storage_mb                   = 5120
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  administrator_login          = var.admin_login
  administrator_login_password = var.admin_password
  version                      = "9.5"
  ssl_enforcement_enabled      = true

  create_mode               = "Replica"
  creation_source_server_id = azurerm_postgresql_server.primary.id
}

resource "azurerm_postgresql_database" "database" {
  depends_on = [azurerm_postgresql_server.primary]

  count = var.create_database ? 1 : 0

  name                = var.database_name
  resource_group_name = var.rg_name
  server_name         = azurerm_postgresql_server.primary.name
  charset             = "UTF8"
  collation           = "en-GB"
}

resource "azurerm_postgresql_firewall_rule" "firewall-primary" {
  name                = var.firewall_rule_name
  resource_group_name = var.rg_name
  server_name         = azurerm_postgresql_server.primary.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "255.255.255.255"
}

resource "azurerm_postgresql_firewall_rule" "firewall-replica" {
  count               = var.create_replica ? 1 : 0
  name                = "${var.firewall_rule_name}-replica"
  resource_group_name = var.rg_name
  server_name         = azurerm_postgresql_server.replica[0].name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "255.255.255.255"
}
