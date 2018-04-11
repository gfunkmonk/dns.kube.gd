
Docker image for a DNS server implementing ``xip.io`` / ``nip.io`` style
DNS wildcards, more conventional glob style DNS wildcard mappings, as well
as pass through for all other lookups.

``xip.io`` and ``nip.io`` work great, the functionality here is the same
and is ultimately because ingress requries hostname matches and you can
no longer generate ACME / Lets Encrypt certificates with xip or nip.

# Getting Started

Any URL that ends with `dns.kube.gd` will map to the embedded IP address.
For example:

 * app.**10**.**0**.**0**.**110**.dns.kube.gd => 10.0.0.110
 * hello.**172**.**168**.**12**.**2**.dns.kube.gd => 172.168.12.2
 * sub.domain.**192**.**168**.**250**.**6**.dns.kube.gd => 192.168.250.6

# kube.gd

Kube Gud is a collection of scripts and services, provided for free, to help
progress Kubernetes usage (esp. when running your own cluster)
