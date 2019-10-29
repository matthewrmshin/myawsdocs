const { spawn } = require('child_process');
const { tmpdir } = require('os');
const path = require('path');
const process = require('process');

exports.handler = async function(event, context) {
  if (context && context.hasOwnProperty('awsRequestId')) {
    console.log(context.awsRequestId);
  }
  const mybin = spawn(path.join(__dirname, 'index.bin'), [], {'cwd': tmpdir()});
  mybin.stdout.on('data', (data) => {
    console.log(`index.bin says ${data}`);
  });
  mybin.stderr.on('data', (data) => {
    console.error(`index.bin says: ${data}`);
  });
  mybin.on('close', (code) => {
    console.log(`index.bin returns ${code}`);
  });
  return mybin;
}

if (require.main == module) {
  exports.handler();
}
