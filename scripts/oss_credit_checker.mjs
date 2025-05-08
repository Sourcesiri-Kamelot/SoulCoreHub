// ✅ LIVE — ESM version for Node.js 23+
import { exec } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import open from 'open'; // Requires open@10.x

exec('npm fund --json', async (err, stdout, stderr) => {
  if (err || stderr) {
    console.error('❌ Error fetching funding info:', err || stderr);
    return;
  }

  const fundData = JSON.parse(stdout);
  const packages = Object.entries(fundData);

  if (!packages.length) {
    console.log("✅ No packages requesting funding found.");
    return;
  }

  const output = packages.map(([pkg, details]) => {
    return `📦 ${pkg}\n🔗 ${details.url || 'N/A'}\n`;
  }).join('\n');

  console.log("💠 Open Source Projects Asking for Support:\n");
  console.log(output);

  writeFileSync('logs/open_source_credits.txt', output);

  // Auto-open links
  for (const [, details] of packages) {
    if (details?.url) {
      await open(details.url);
    }
  }
});
