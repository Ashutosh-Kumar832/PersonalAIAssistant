listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = 1
}

storage "file" {
  path = "./vault_data"
}

disable_mlock = true
