
DNS service for implementing ``xip.io`` / ``nip.io`` style DNS wildcards,
more conventional glob style DNS wildcard mappings, as well as pass through
for all other lookups.

``xip.io`` and ``nip.io`` work great, the functionality here is the same
and is ultimately better as Kubernetes ingress requries hostname matches
and you can no longer generate ACME / Lets Encrypt certificates with xip
or nip. There have also been a lot of outages with both services that
make it decent for developers but unreliable for CI or demos.

# Getting Started

Any URL that ends with `kube.gd` will map to the embedded IP address.
For example:

<ul class="code">
  <li>          app.<strong>10</strong>.<strong>0</strong>.<strong>0</strong>.<strong>110</strong>.kube.gd ⇨ 10.0.0.110</li>
  <li>      hello.<strong>172</strong>.<strong>168</strong>.<strong>12</strong>.<strong>2</strong>.kube.gd ⇨ 172.168.12.2</li>
  <li>sub.domain.<strong>192</strong>.<strong>168</strong>.<strong>250</strong>.<strong>6</strong>.kube.gd ⇨ 192.168.250.6</li>
</ul>

# Advanced Setup

While the above is the minimum required to get a working setup, there are more
advanced features for persisting a configurations. These are not required and
are completely optional.

## Registration

To avoid a single point of failure with addresses and to make things more
fun, you can register a single sub-domain by running ``kubegd/dns-register:latest``.
This will create a single subdomain, point to all works with an ingress-controller.

```
kubectl apply -f https://dns.kube.gd/register.yaml
kubectl logs -f deploy/kube.gd
```

The log will report your address name:

```
👋 Attempting to register address for 00df6fa7-62b6-43f9-b7aa-8c8214e6da73...
👍 00df6fa7-62b6-43f9-b7aa-8c8214e6da73 registered as 00df6fa7.kube.gd
💪 Adding 10.0.0.12 to 00df6fa7.kube.gd 👍
💪 Adding 10.0.1.82 to 00df6fa7.kube.gd 👍
💪 Adding 10.0.0.96 to 00df6fa7.kube.gd 👍
☝ Testing resolution...👍
👌 00df6fa7.kube.gd has been configured!


👉 You can now create ingress resources using *.00df6fa7.kube.gd
```

From this point forward you can use the new address instead of a full IP space.

<ul class="code">
  <li>       app.<strong>00df6fa7</strong>.kube.gd ⇨ 10.0.0.12, 10.0.1.82, 10.0.0.96</li>
  <li>     hello.<strong>00df6fa7</strong>.kube.gd ⇨ 10.0.0.12, 10.0.1.82, 10.0.0.96</li>
  <li>sub.domain.<strong>00df6fa7</strong>.kube.gd ⇨ 10.0.0.12, 10.0.1.82, 10.0.0.96</li>
</ul>

# What is kube.gd?

Kube Gud is a collection of scripts and services, provided for free, to help
progress Kubernetes usage (esp. when running your own cluster)
