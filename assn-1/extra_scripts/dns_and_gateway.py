import netifaces
import dns.resolver

gateways = netifaces.gateways()
default_gateway = gateways['default'][netifaces.AF_INET][0]
print("default gateway: ", default_gateway)

resolver = dns.resolver.Resolver()
dns_nameservers = resolver.nameservers
print("DNS nameservers: ", dns_nameservers)
