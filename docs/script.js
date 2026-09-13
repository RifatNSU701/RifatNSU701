// ---------- Tech matrix (clickable real logos via Simple Icons CDN) ----------
const ICON = (slug) => `https://cdn.simpleicons.org/${slug}/2FD9E8`;

function chip(label, slug, url) {
  const img = slug
    ? `<img src="${ICON(slug)}" alt="${label} logo" onerror="this.style.display='none'">`
    : `<span class="icon-fallback">●</span>`;
  return `<a class="icon-chip" href="${url}" target="_blank" rel="noopener noreferrer" title="Open ${label} website">${img}<span>${label}</span><span class="external-mark">↗</span></a>`;
}

const matrices = {
  "matrix-secops": [
    ["Wazuh", "wazuh", "https://wazuh.com/"],
    ["Splunk", "splunk", "https://www.splunk.com/"],
    ["Elastic Security", "elastic", "https://www.elastic.co/security"],
  ],
  "matrix-sectest": [
    ["Nmap", "nmap", "https://nmap.org/"],
    ["Metasploit", null, "https://www.metasploit.com/"],
    ["Burp Suite", "burpsuite", "https://portswigger.net/burp"],
  ],
  "matrix-netsec": [
    ["pfSense", null, "https://www.pfsense.org/"],
    ["Wireshark", "wireshark", "https://www.wireshark.org/"],
    ["VPN", null, "https://www.cloudflare.com/learning/access-management/what-is-a-vpn/"],
  ],
  "matrix-net": [
    ["Cisco IOS", "cisco", "https://www.cisco.com/c/en/us/products/ios-nx-os-software/index.html"],
    ["Packet Tracer", "cisco", "https://www.netacad.com/cisco-packet-tracer"],
  ],
  "matrix-linux": [
    ["Kali Linux", "kalilinux", "https://www.kali.org/"],
    ["Ubuntu", "ubuntu", "https://ubuntu.com/"],
    ["Linux Server", "linux", "https://www.linux.org/"],
    ["Bash", "gnubash", "https://www.gnu.org/software/bash/"],
    ["SSH", "openssh", "https://www.openssh.com/"],
  ],
  "matrix-iot": [
    ["MQTT", "mqtt", "https://mqtt.org/"],
    ["BLE", "bluetooth", "https://www.bluetooth.com/"],
  ],
  "matrix-prog": [
    ["Python", "python", "https://www.python.org/"],
    ["Java", "openjdk", "https://www.java.com/"],
    ["C++", "cplusplus", "https://isocpp.org/"],
    ["Bash", "gnubash", "https://www.gnu.org/software/bash/"],
  ],
  "matrix-dev": [
    ["Git", "git", "https://git-scm.com/"],
    ["GitHub", "github", "https://github.com/"],
    ["VirtualBox", "virtualbox", "https://www.virtualbox.org/"],
  ],
};

for (const [id, items] of Object.entries(matrices)) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = items.map(([label, slug, url]) => chip(label, slug, url)).join("");
}

// ---------- Reveal-on-load ----------
const revealTargets = document.querySelectorAll(".reveal");
const io = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("in");
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.08 });
revealTargets.forEach((el) => io.observe(el));

// ---------- Count-up for stat tiles ----------
function countUp(el, target) {
  if (target === null || target === undefined) { el.textContent = "—"; return; }
  const duration = 900;
  const start = performance.now();
  function tick(now) {
    const p = Math.min((now - start) / duration, 1);
    el.textContent = Math.floor(p * target).toLocaleString();
    if (p < 1) requestAnimationFrame(tick);
    else el.textContent = target.toLocaleString();
  }
  requestAnimationFrame(tick);
}

// ---------- Load real data ----------
async function loadStats() {
  try {
    const res = await fetch("data/stats.json", { cache: "no-store" });
    const data = await res.json();

    if (data.pending) {
      document.getElementById("lastSync").textContent =
        "No sync has run yet. Trigger the 'Sync GitHub Intelligence Data' Action to populate this dashboard with real numbers.";
    } else {
      document.getElementById("lastSync").textContent =
        `Last synced ${new Date(data.generated_at).toLocaleString()}`;
    }

    countUp(document.getElementById("statRepos"), data.totals.repositories);
    countUp(document.getElementById("statStars"), data.totals.stars);
    countUp(document.getElementById("statForks"), data.totals.forks);
    countUp(document.getElementById("statPRs"), data.totals.pull_requests);

    // Language chart
    const langEl = document.getElementById("langChart");
    if (data.languages && data.languages.length) {
      new Chart(langEl, {
        type: "doughnut",
        data: {
          labels: data.languages.map((l) => l.name),
          datasets: [{
            data: data.languages.map((l) => l.percent),
            backgroundColor: ["#2fd9e8", "#ffb84d", "#ff4d8d", "#3ddc84", "#7c8a97", "#5b8def", "#c792ea"],
            borderColor: "#0a1016",
            borderWidth: 2,
          }],
        },
        options: {
          plugins: { legend: { position: "right", labels: { color: "#dce6ee", font: { family: "JetBrains Mono", size: 11 } } } },
        },
      });
    } else {
      document.getElementById("langPending").style.display = "block";
    }

    // Activity feed
    const list = document.getElementById("activityList");
    if (data.recent_activity && data.recent_activity.length) {
      list.innerHTML = data.recent_activity
        .map((a) => {
          const when = new Date(a.created_at).toLocaleDateString();
          return `<li><span class="t">${when}</span><span>${a.type.replace("Event", "")} — ${a.repo || ""}</span></li>`;
        })
        .join("");
    } else {
      list.innerHTML = "<li>No activity recorded yet — waiting for first sync.</li>";
    }
  } catch (err) {
    console.error("Failed to load stats.json", err);
    document.getElementById("lastSync").textContent = "Could not load stats.json.";
  }
}

loadStats();
