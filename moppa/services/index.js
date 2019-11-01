const { spawnSync } = require('child_process');
const path = require('path');
const process = require('process');

exports.handler = async function(event, context) {
  if (context && context.hasOwnProperty('awsRequestId')) {
    console.log(`request ID: ${context.awsRequestId}`);
  }
  const mybinpath = path.join(__dirname, 'index.bin')
  console.log(`executable: ${mybinpath}`);
  const { stdout, stderr, error } = spawnSync(mybinpath, [], {'env': {'LD_LIBRARY_PATH': `${__dirname}:/lib64:/usr/lib64`}});
  console.log(`index.bin says ${stdout}`);
  console.error(`index.bin says: ${stderr}`);
  if (error) {
    console.error(`index.bin returns ${error}`);
  }
  console.log(`executable done: ${mybinpath}`);
  return;
}

if (require.main == module) {
  exports.handler();
}