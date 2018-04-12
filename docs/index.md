
Docker image for a DNS server implementing ``xip.io`` / ``nip.io`` style
DNS wildcards, more conventional glob style DNS wildcard mappings, as well
as pass through for all other lookups.

``xip.io`` and ``nip.io`` work great, the functionality here is the same
and is ultimately because ingress requries hostname matches and you can
no longer generate ACME / Lets Encrypt certificates with xip or nip.

# Getting Started

Any URL that ends with `dns.kube.gd` will map to the embedded IP address.
For example:

 * app.**10**.**0**.**0**.**110**.kube.gd => 10.0.0.110
 * hello.**172**.**168**.**12**.**2**.kube.gd => 172.168.12.2
 * sub.domain.**192**.**168**.**250**.**6**.kube.gd => 192.168.250.6

# Registering

To avoid a single point of failure with addresses and to make things more
fun, you can register a single sub-domain by running ``kubegd/dns-register:latest``.
This will create a single subdomain, point to all works with an ingress-controller.

```
kubectl apply -f https://dns.kube.gd/register.yaml
kubectl logs -f deploy/kube.gd
```

The log will report your address name:

```
Attempting to register address for 00df6fa7-62b6-43f9-b7aa-8c8214e6da73...
00df6fa7-62b6-43f9-b7aa-8c8214e6da73 registered as 00df6fa7.kube.gd
Adding 10.0.0.12 to 00df6fa7.kube.gd
Adding 10.0.1.82 to 00df6fa7.kube.gd
Adding 10.0.0.96 to 00df6fa7.kube.gd
Testing resolution...
00df6fa7.kube.gd has been configured!
.
.
.
You can now create ingress resources at *.00df6fa7.kube.gd
```

From this point forward you can use the new address instead of a full IP space.

 * app.**00df6fa7**.kube.gd => 10.0.0.12, 10.0.1.82, 10.0.0.96
 * hello.**00df6fa7**.kube.gd => 10.0.0.12, 10.0.1.82, 10.0.0.96
 * sub.domain.**00df6fa7**.kube.gd => 10.0.0.12, 10.0.1.82, 10.0.0.96

# What is kube.gd?

Kube Gud is a collection of scripts and services, provided for free, to help
progress Kubernetes usage (esp. when running your own cluster)
