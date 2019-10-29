const { spawn } = require('child_process');
const path = require('path');
const process = require('process');

exports.handler = async function(event, context) {
  if (context && context.hasOwnProperty('awsRequestId')) {
    console.log(`request ID: ${context.awsRequestId}`);
  }
  mybinpath = path.join(__dirname, 'index.bin')
  console.log(`executable: ${mybinpath}`);
  const mybin = spawn(mybinpath);
  mybin.stdout.on('data', (data) => {
    console.log(`index.bin says ${data}`);
  });
  mybin.stderr.on('data', (data) => {
    console.error(`index.bin says: ${data}`);
  });
  mybin.on('close', (code) => {
    console.log(`index.bin returns ${code}`);
  });
  console.log(`executable launched: ${mybinpath}`);
  return mybin;
}

if (require.main == module) {
  exports.handler();
}
