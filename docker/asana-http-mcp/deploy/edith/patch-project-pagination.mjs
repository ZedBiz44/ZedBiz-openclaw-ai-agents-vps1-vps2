import fs from 'node:fs';
const file=process.argv[2]??'/app/dist/index.js';
const old="async getTasksForProject(projectId, opts = {}) {\n    const response = await this.tasks.getTasksForProject(projectId, opts);\n    return response.data;\n  }";
const replacement="async getTasksForProject(projectId, opts = {}) {\n    const rows = [], seen = new Set();\n    let offset = opts.offset;\n    for (let page = 0; page < 1000; page++) {\n      const response = await this.tasks.getTasksForProject(projectId, {...opts, limit: opts.limit ?? 100, ...(offset ? {offset} : {})});\n      if (!Array.isArray(response.data)) throw new Error(\"Invalid project task page\");\n      rows.push(...response.data);\n      offset = response.next_page?.offset;\n      if (!offset) return rows;\n      if (seen.has(offset)) throw new Error(\"Repeated project task cursor\");\n      seen.add(offset);\n    }\n    throw new Error(\"Project task pagination limit exceeded; no partial results returned\");\n  }";
const source=fs.readFileSync(file,'utf8');
if(source.split(old).length!==2)throw new Error('Unexpected bundle; refuse project pagination patch');
fs.writeFileSync(file,source.replace(old,replacement));
console.log('Project task reads now return all pages or fail without partial output');
