// ---------- Tech matrix (real logos via simple-icons CDN, graceful fallback to text-only) ----------
const ICON = (slug) => `https://cdn.simpleicons.org/${slug}/2FD9E8`;

function chip(label, slug) {
  const img = slug
    ? `<img src="${ICON(slug)}" alt="" onerror="this.remove()">`
    : "";
  return `<span class="icon-chip">${img}${label}</span>`;
}

const matrices = {
  "matrix-secops": [["Wazuh", "wazuh"], ["Splunk", "splunk"], ["Elastic Security", "elastic"]],
  "matrix-sectest": [["Nmap", "nmap"], ["Metasploit", null], ["Burp Suite", "burpsuite"]],
  "matrix-netsec": [["pfSense", null], ["Wireshark", "wireshark"], ["VPN", null]],
  "matrix-net": [["Cisco IOS", "cisco"], ["Packet Tracer", "cisco"]],
  "matrix-linux": [["Kali Linux", "kalilinux"], ["Ubuntu", "ubuntu"], ["Linux Server", "linux"], ["Bash", "gnubash"], ["SSH", "openssh"]],
  "matrix-iot": [["MQTT", "mqtt"], ["BLE", "bluetooth"]],
  "matrix-prog": [["Python", "python"], ["Java", "openjdk"], ["C++", "cplusplus"], ["Bash", "gnubash"]],
  "matrix-dev": [["Git", "git"], ["GitHub", "github"], ["VirtualBox", "virtualbox"]],
};

for (const [id, items] of Object.entries(matrices)) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = items.map(([label, slug]) => chip(label, slug)).join("");
}

// ---------- Reveal-on-load (single orchestrated pass, staggered) ----------
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
