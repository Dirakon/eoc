// Copyright (c) 2022-2025 Objectionary.com
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

/*
 * SPDX-FileCopyrightText: Copyright (c) 2022-2025 Objectionary.com
 * SPDX-License-Identifier: MIT
 */

const fs = require('fs');
const path = require('path');
const execSync = require('child_process').execSync;
const {runSync, assertFilesExist, weAreOnline} = require('../../helpers');
const version = '0.6.11';

describe('jeo:assemble', function() {
  before(weAreOnline);

  it('converts XMIR files to CLASS files', function(done) {
    const home = path.resolve('temp/test-jeo-assemble/simple');
    fs.rmSync(home, {recursive: true, force: true});
    fs.mkdirSync(home, {recursive: true});
    fs.writeFileSync(path.resolve(home, 'Foo.java'), 'package bar; class Foo {}');
    execSync(`javac ${path.resolve(home, 'Foo.java')}`);
    runSync([
      'jeo:disassemble',
      '--verbose',
      `--jeo-version=${version}`,
      '--classes', home,
      '--xmirs', home,
    ]);
    fs.rmSync(path.resolve(home, 'Foo.class'), {recursive: true, force: true});
    fs.rmSync(path.resolve(home, 'Foo.java'), {recursive: true, force: true});
    const stdout = runSync([
      'jeo:assemble',
      '--verbose',
      `--jeo-version=${version}`,
      '--xmirs', home,
      '--unrolled', path.resolve(home, 'unrolled'),
      '--classes', home,
    ]);
    assertFilesExist(
      stdout, home,
      [
        'bar/Foo.class',
        'bar/Foo.xmir'
      ]
    );
    done();
  });
});
