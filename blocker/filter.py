from python_hosts import Hosts, HostsEntry
import os
import platform
import requests
from bs4 import BeautifulSoup
from .utils import load_json_file, save_json_file
import re
import subprocess
import time


class ContentFilter:
    def __init__(self):
        self.system = platform.system()
        if self.system == "Windows":
            self.hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        else:
            self.hosts_path = "/etc/hosts"

        # Store original hosts file content
        with open(self.hosts_path, "r") as f:
            self.original_hosts = f.read()

        self.hosts = Hosts(path=self.hosts_path)

        # Load keywords
        self.keywords_file = "blocked_keywords.json"
        self.keywords = load_json_file(
            self.keywords_file, default={"explicit": [], "moderate": []}
        )

        self.is_active = False

    def flush_dns_cache(self):
        """Flush the DNS cache to ensure hosts file changes take effect"""
        try:
            if self.system == "Windows":
                # Run multiple DNS-related commands to ensure cache is cleared
                subprocess.run(
                    ["ipconfig", "/flushdns"], check=True, capture_output=True
                )
                subprocess.run(
                    ["ipconfig", "/release"], check=True, capture_output=True
                )
                subprocess.run(["ipconfig", "/renew"], check=True, capture_output=True)
                time.sleep(2)  # Give some time for DNS to update
            else:
                # For Linux/Mac, you might need different commands or sudo
                pass
            return True
        except Exception as e:
            print(f"Error flushing DNS cache: {e}")
            return False

    def block_url(self, url):
        """Add a URL to the hosts file to block it"""
        try:
            # Remove http:// or https:// if present
            url = url.replace("http://", "").replace("https://", "")
            # Remove path components, keep only domain or IP
            url = url.split("/")[0]

            # Check if the URL is an IP address
            is_ip = all(
                part.isdigit() and 0 <= int(part) <= 255
                for part in url.split(".")
                if part
            )

            if is_ip:
                # For IP addresses, map localhost to the IP
                entries = [
                    HostsEntry(entry_type="ipv4", address="127.0.0.1", names=[url])
                ]
            else:
                # For domains, block both www and non-www versions
                urls_to_block = [url]
                if not url.startswith("www."):
                    urls_to_block.append("www." + url)

                entries = [
                    HostsEntry(entry_type="ipv4", address="127.0.0.1", names=[u])
                    for u in urls_to_block
                ]

            self.hosts.add(entries)
            if self.is_active:
                self.hosts.write()
                self.flush_dns_cache()
            return True
        except Exception as e:
            print(f"Error blocking URL: {e}")
            return False

    def unblock_url(self, url):
        """Remove a URL from the hosts file"""
        try:
            url = url.replace("http://", "").replace("https://", "")
            url = url.split("/")[0]

            # Check if the URL is an IP address
            is_ip = all(
                part.isdigit() and 0 <= int(part) <= 255
                for part in url.split(".")
                if part
            )

            if is_ip:
                # For IP addresses, just remove the entry
                self.hosts.remove_all_matching(name=url)
            else:
                # For domains, remove both www and non-www versions
                if url.startswith("www."):
                    base_url = url[4:]
                    self.hosts.remove_all_matching(name=url)
                    self.hosts.remove_all_matching(name=base_url)
                else:
                    self.hosts.remove_all_matching(name=url)
                    self.hosts.remove_all_matching(name="www." + url)

            if self.is_active:
                self.hosts.write()
                self.flush_dns_cache()
            return True
        except Exception as e:
            print(f"Error unblocking URL: {e}")
            return False

    def get_blocked_urls(self):
        """Get list of currently blocked URLs from hosts file"""
        blocked = []
        for entry in self.hosts.entries:
            if entry.entry_type == "ipv4" and entry.address == "127.0.0.1":
                blocked.extend(entry.names)
        return blocked

    def enable_blocking(self):
        """Enable content blocking by writing to hosts file"""
        try:
            # Write current hosts configuration
            self.hosts.write()
            self.is_active = True
            self.flush_dns_cache()
            return True
        except Exception as e:
            print(f"Error enabling blocking: {e}")
            return False

    def disable_blocking(self):
        """Disable content blocking by restoring original hosts file"""
        try:
            # First, restore the original hosts file
            with open(self.hosts_path, "w") as f:
                f.write(self.original_hosts)

            # Reset the hosts object to match the original state
            self.hosts = Hosts(path=self.hosts_path)
            self.is_active = False

            # Aggressively flush DNS cache
            self.flush_dns_cache()

            # Double-check if file was restored correctly
            with open(self.hosts_path, "r") as f:
                current_content = f.read()
                if current_content.strip() != self.original_hosts.strip():
                    raise Exception("Hosts file not properly restored")

            return True
        except Exception as e:
            print(f"Error disabling blocking: {e}")
            return False

    def add_keyword(self, keyword, category="explicit"):
        """Add a keyword to block"""
        if category not in self.keywords:
            self.keywords[category] = []
        if keyword not in self.keywords[category]:
            self.keywords[category].append(keyword)
            save_json_file(self.keywords_file, self.keywords)
            return True
        return False

    def remove_keyword(self, keyword, category="explicit"):
        """Remove a keyword from blocking"""
        if category in self.keywords and keyword in self.keywords[category]:
            self.keywords[category].remove(keyword)
            save_json_file(self.keywords_file, self.keywords)
            return True
        return False

    def get_keywords(self, category=None):
        """Get list of blocked keywords"""
        if category:
            return self.keywords.get(category, [])
        return self.keywords

    def check_content(self, url, content):
        """Check if content contains blocked keywords and return detailed scores"""
        try:
            # Convert content to lowercase for case-insensitive matching
            content = content.lower()
            total_words = len(content.split())

            # Initialize scores dictionary
            scores = {
                "explicit": 0.0,
                "moderate": 0.0,
                "safe": 1.0,  # Start with assumption of safe
                "matches": {"explicit": [], "moderate": []},
            }

            # Check explicit keywords
            explicit_keywords = self.keywords.get("explicit", [])
            for keyword in explicit_keywords:
                if keyword.lower() in content:
                    matches = len(
                        re.findall(r"\b" + re.escape(keyword.lower()) + r"\b", content)
                    )
                    if matches > 0:
                        scores["matches"]["explicit"].append((keyword, matches))
                        # Each explicit keyword hit reduces safety score significantly
                        scores["explicit"] += 0.3 * matches

            # Check moderate keywords
            moderate_keywords = self.keywords.get("moderate", [])
            for keyword in moderate_keywords:
                if keyword.lower() in content:
                    matches = len(
                        re.findall(r"\b" + re.escape(keyword.lower()) + r"\b", content)
                    )
                    if matches > 0:
                        scores["matches"]["moderate"].append((keyword, matches))
                        # Each moderate keyword hit has less impact
                        scores["moderate"] += 0.15 * matches

            # Normalize scores
            total_score = scores["explicit"] + scores["moderate"]
            if total_score > 1.0:
                scores["explicit"] = min(1.0, scores["explicit"])
                scores["moderate"] = min(1.0, scores["moderate"])
                scores["safe"] = 0.0
            else:
                scores["safe"] = max(0.0, 1.0 - total_score)

            # Determine if content should be blocked
            should_block = scores["explicit"] >= 0.3 or scores["moderate"] >= 0.45

            return should_block, scores

        except Exception as e:
            print(f"Error checking content: {e}")
            return False, {
                "explicit": 0.0,
                "moderate": 0.0,
                "safe": 1.0,
                "matches": {"explicit": [], "moderate": []},
            }

    def check_webpage(self, url):
        """Check if a webpage contains inappropriate content"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Check text content
            text_content = soup.get_text()
            is_inappropriate, scores = self.check_content(url, text_content)

            # Return both the blocking decision and the scores
            return is_inappropriate, scores

        except Exception as e:
            print(f"Error checking webpage: {e}")
            return False, {
                "explicit": 0.0,
                "moderate": 0.0,
                "safe": 1.0,
                "matches": {"explicit": [], "moderate": []},
            }
