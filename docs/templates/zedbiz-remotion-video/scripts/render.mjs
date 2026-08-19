import {existsSync, mkdirSync, readFileSync} from 'node:fs';
import {dirname, isAbsolute, resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const configArg = process.argv[2] ?? 'examples/smoke.json';
const outputArg = process.argv[3] ?? 'outputs/zedbiz-video.mp4';
const configPath = isAbsolute(configArg) ? configArg : resolve(projectRoot, configArg);
const outputPath = isAbsolute(outputArg) ? outputArg : resolve(projectRoot, outputArg);

if (!existsSync(configPath)) {
  throw new Error(`Project configuration not found: ${configPath}`);
}

const project = JSON.parse(readFileSync(configPath, 'utf8'));
if (!Array.isArray(project.scenes) || project.scenes.length === 0) {
  throw new Error('Project configuration must contain at least one scene.');
}

mkdirSync(dirname(outputPath), {recursive: true});

const remotionCli = resolve(
  projectRoot,
  'node_modules',
  '@remotion',
  'cli',
  'remotion-cli.js',
);
const args = [
  'render',
  resolve(projectRoot, 'src', 'index.ts'),
  'ZedBizVideo',
  outputPath,
  `--props=${configPath}`,
  '--codec=h264',
];

if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  args.push(`--browser-executable=${process.env.REMOTION_BROWSER_EXECUTABLE}`);
}

const result = spawnSync(process.execPath, [remotionCli, ...args], {
  cwd: projectRoot,
  stdio: 'inherit',
  env: process.env,
});

if (result.error) throw result.error;
process.exit(result.status ?? 1);
