from typing import Optional
import ipaddress
import dns.resolver
import requests


# Constants
FETCH_TIMEOUT = 5
GCP_METADATA_ZONE = 'http://169.254.169.254/computeMetadata/v1/instance/zone'
GCP_METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
AWS_IP_RANGE = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
DNS_TARGET = 'o-o.myaddr.l.google.com'


def find_aws_region_from_ip() -> Optional[str]:
    """Find AWS region from public IPV4 address (if in AWS).

    If the public IPV4 address is not located in an AWS EC2 IPV4 region then
    return None.

    Returns:
         The AWS region if found. None otherwise.
    """

    # Fetch the AWS IP-Ranges JSON
    ip_ranges_res = requests.get(AWS_IP_RANGE, timeout=FETCH_TIMEOUT)
    ip_ranges = ip_ranges_res.json()

    # Extract the CIDRs for EC2 for all regions (IPV4 only)
    prefixes = filter(lambda prefix: prefix['service'] == 'EC2',
                      ip_ranges['prefixes'])

    # Get IP of this instance (use the first result if there are more than one)
    ip = str(dns.resolver.query(DNS_TARGET, 'TXT')[0]).strip('"')
    ip_addr = ipaddress.ip_address(ip)

    # Determine if the IP address of the instance is in any of the CIDR ranges
    for prefix in prefixes:
        cidr = ipaddress.ip_network(prefix['ip_prefix'])

        # If a matching CIDR range is found, return region
        if ip_addr in cidr:
            return prefix['region']

    # If this IP is not found in any EC2 region, return None
    return None


def find_gcp_region_from_instance_metadata() -> Optional[str]:
    """Find GCP region from GCP instance metadata service (if in GCP).

    If the GCP instance metadata is not accessible then this instance is not
    located in GCP and thus returns None.
    return None.

    Returns:
         The GCP region if found. None otherwise.
    """

    # Try and query GCP instance metadata
    try:
        zone_res = requests.get(GCP_METADATA_ZONE,
                                headers=GCP_METADATA_HEADERS,
                                timeout=FETCH_TIMEOUT)
    # Fail fast on any exception
    except Exception:
        return None

    # If GCP instance metadata was accessible, return region
    if zone_res.ok:
        # Get the region from the metadata
        zone = zone_res.text.split('/')[-1]
        return '-'.join(zone.split('-')[:-1])

    # If the instance metadata was not accessible, return None
    return None


def main():

    # AWS
    region = find_aws_region_from_ip()
    if region is not None:
        print(f'Cloud: AWS, Region: {region}')
        return

    # GCP
    region = find_gcp_region_from_instance_metadata()
    if region is not None:
        print(f'Cloud: GCP, Region: {region}')
        return

    # Azure

    # Unknown
    print('Cloud: unknown, Region: unknown')


if __name__ == '__main__':
    main()






# Look for the IP address of this node in AWS IP ranges
print(find_gcp_region_from_instance_metadata())
print()
