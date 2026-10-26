const fs=require('fs');
const target=process.argv[2];
const before=fs.readFileSync(target,'utf8').replace(/\r\n/g,'\n');
const old=`      try {
        const timeout = new Promise((resolve2) => {
          setTimeout(() => resolve2(void 0), RECALL_TIMEOUT_MS);
        });
        const result = await Promise.race([
          recallWork(),
          timeout.then(() => {
            api.logger.warn(
              \`openclaw-mem0: recall timed out after \${RECALL_TIMEOUT_MS}ms, skipping\`
            );
            return void 0;
          })
        ]);
        return result;
      } catch (err) {
        api.logger.warn(\`openclaw-mem0: recall failed: \${String(err)}\`);
      }`;
const replacement=`      // Cody 2026-10-26: cancel the losing timer; report only a real deadline.
      let recallTimeout;
      try {
        const timeout = new Promise((resolve2) => {
          recallTimeout = setTimeout(() => {
            api.logger.warn(
              \`openclaw-mem0: recall timed out after \${RECALL_TIMEOUT_MS}ms, skipping\`
            );
            resolve2(void 0);
          }, RECALL_TIMEOUT_MS);
        });
        return await Promise.race([recallWork(), timeout]);
      } catch (err) {
        api.logger.warn(\`openclaw-mem0: recall failed: \${String(err)}\`);
      } finally {
        clearTimeout(recallTimeout);
      }`;
if(before.includes(replacement)){console.log('already-patched');process.exit(0)}
if(before.split(old).length!==2)throw Error('Expected exactly one reviewed timer block');
fs.writeFileSync(target,before.replace(old,replacement));console.log('patched');

