// node_modules/@material/material-color-utilities/utils/math_utils.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
function signum(num3) {
  if (num3 < 0) {
    return -1;
  } else if (num3 === 0) {
    return 0;
  } else {
    return 1;
  }
}
function lerp(start, stop, amount) {
  return (1 - amount) * start + amount * stop;
}
function clampInt(min, max, input) {
  if (input < min) {
    return min;
  } else if (input > max) {
    return max;
  }
  return input;
}
function clampDouble(min, max, input) {
  if (input < min) {
    return min;
  } else if (input > max) {
    return max;
  }
  return input;
}
function sanitizeDegreesInt(degrees) {
  degrees = degrees % 360;
  if (degrees < 0) {
    degrees = degrees + 360;
  }
  return degrees;
}
function sanitizeDegreesDouble(degrees) {
  degrees = degrees % 360;
  if (degrees < 0) {
    degrees = degrees + 360;
  }
  return degrees;
}
function rotationDirection(from, to) {
  const increasingDifference = sanitizeDegreesDouble(to - from);
  return increasingDifference <= 180 ? 1 : -1;
}
function differenceDegrees(a, b) {
  return 180 - Math.abs(Math.abs(a - b) - 180);
}
function matrixMultiply(row, matrix) {
  const a = row[0] * matrix[0][0] + row[1] * matrix[0][1] + row[2] * matrix[0][2];
  const b = row[0] * matrix[1][0] + row[1] * matrix[1][1] + row[2] * matrix[1][2];
  const c2 = row[0] * matrix[2][0] + row[1] * matrix[2][1] + row[2] * matrix[2][2];
  return [a, b, c2];
}

// node_modules/@material/material-color-utilities/utils/color_utils.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var SRGB_TO_XYZ = [
  [0.41233895, 0.35762064, 0.18051042],
  [0.2126, 0.7152, 0.0722],
  [0.01932141, 0.11916382, 0.95034478]
];
var XYZ_TO_SRGB = [
  [
    3.2413774792388685,
    -1.5376652402851851,
    -0.49885366846268053
  ],
  [
    -0.9691452513005321,
    1.8758853451067872,
    0.04156585616912061
  ],
  [
    0.05562093689691305,
    -0.20395524564742123,
    1.0571799111220335
  ]
];
var WHITE_POINT_D65 = [95.047, 100, 108.883];
function argbFromRgb(red, green, blue) {
  return (255 << 24 | (red & 255) << 16 | (green & 255) << 8 | blue & 255) >>> 0;
}
function argbFromLinrgb(linrgb) {
  const r2 = delinearized(linrgb[0]);
  const g = delinearized(linrgb[1]);
  const b = delinearized(linrgb[2]);
  return argbFromRgb(r2, g, b);
}
function redFromArgb(argb) {
  return argb >> 16 & 255;
}
function greenFromArgb(argb) {
  return argb >> 8 & 255;
}
function blueFromArgb(argb) {
  return argb & 255;
}
function argbFromXyz(x, y, z) {
  const matrix = XYZ_TO_SRGB;
  const linearR = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z;
  const linearG = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z;
  const linearB = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z;
  const r2 = delinearized(linearR);
  const g = delinearized(linearG);
  const b = delinearized(linearB);
  return argbFromRgb(r2, g, b);
}
function xyzFromArgb(argb) {
  const r2 = linearized(redFromArgb(argb));
  const g = linearized(greenFromArgb(argb));
  const b = linearized(blueFromArgb(argb));
  return matrixMultiply([r2, g, b], SRGB_TO_XYZ);
}
function labFromArgb(argb) {
  const linearR = linearized(redFromArgb(argb));
  const linearG = linearized(greenFromArgb(argb));
  const linearB = linearized(blueFromArgb(argb));
  const matrix = SRGB_TO_XYZ;
  const x = matrix[0][0] * linearR + matrix[0][1] * linearG + matrix[0][2] * linearB;
  const y = matrix[1][0] * linearR + matrix[1][1] * linearG + matrix[1][2] * linearB;
  const z = matrix[2][0] * linearR + matrix[2][1] * linearG + matrix[2][2] * linearB;
  const whitePoint = WHITE_POINT_D65;
  const xNormalized = x / whitePoint[0];
  const yNormalized = y / whitePoint[1];
  const zNormalized = z / whitePoint[2];
  const fx = labF(xNormalized);
  const fy = labF(yNormalized);
  const fz = labF(zNormalized);
  const l = 116 * fy - 16;
  const a = 500 * (fx - fy);
  const b = 200 * (fy - fz);
  return [l, a, b];
}
function argbFromLstar(lstar) {
  const y = yFromLstar(lstar);
  const component = delinearized(y);
  return argbFromRgb(component, component, component);
}
function lstarFromArgb(argb) {
  const y = xyzFromArgb(argb)[1];
  return 116 * labF(y / 100) - 16;
}
function yFromLstar(lstar) {
  return 100 * labInvf((lstar + 16) / 116);
}
function lstarFromY(y) {
  return labF(y / 100) * 116 - 16;
}
function linearized(rgbComponent) {
  const normalized = rgbComponent / 255;
  if (normalized <= 0.040449936) {
    return normalized / 12.92 * 100;
  } else {
    return Math.pow((normalized + 0.055) / 1.055, 2.4) * 100;
  }
}
function delinearized(rgbComponent) {
  const normalized = rgbComponent / 100;
  let delinearized2 = 0;
  if (normalized <= 31308e-7) {
    delinearized2 = normalized * 12.92;
  } else {
    delinearized2 = 1.055 * Math.pow(normalized, 1 / 2.4) - 0.055;
  }
  return clampInt(0, 255, Math.round(delinearized2 * 255));
}
function whitePointD65() {
  return WHITE_POINT_D65;
}
function labF(t) {
  const e4 = 216 / 24389;
  const kappa = 24389 / 27;
  if (t > e4) {
    return Math.pow(t, 1 / 3);
  } else {
    return (kappa * t + 16) / 116;
  }
}
function labInvf(ft) {
  const e4 = 216 / 24389;
  const kappa = 24389 / 27;
  const ft3 = ft * ft * ft;
  if (ft3 > e4) {
    return ft3;
  } else {
    return (116 * ft - 16) / kappa;
  }
}

// node_modules/@material/material-color-utilities/hct/viewing_conditions.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var ViewingConditions = class _ViewingConditions {
  /**
   * Create ViewingConditions from a simple, physically relevant, set of
   * parameters.
   *
   * @param whitePoint White point, measured in the XYZ color space.
   *     default = D65, or sunny day afternoon
   * @param adaptingLuminance The luminance of the adapting field. Informally,
   *     how bright it is in the room where the color is viewed. Can be
   *     calculated from lux by multiplying lux by 0.0586. default = 11.72,
   *     or 200 lux.
   * @param backgroundLstar The lightness of the area surrounding the color.
   *     measured by L* in L*a*b*. default = 50.0
   * @param surround A general description of the lighting surrounding the
   *     color. 0 is pitch dark, like watching a movie in a theater. 1.0 is a
   *     dimly light room, like watching TV at home at night. 2.0 means there
   *     is no difference between the lighting on the color and around it.
   *     default = 2.0
   * @param discountingIlluminant Whether the eye accounts for the tint of the
   *     ambient lighting, such as knowing an apple is still red in green light.
   *     default = false, the eye does not perform this process on
   *       self-luminous objects like displays.
   */
  static make(whitePoint = whitePointD65(), adaptingLuminance = 200 / Math.PI * yFromLstar(50) / 100, backgroundLstar = 50, surround = 2, discountingIlluminant = false) {
    const xyz = whitePoint;
    const rW = xyz[0] * 0.401288 + xyz[1] * 0.650173 + xyz[2] * -0.051461;
    const gW = xyz[0] * -0.250268 + xyz[1] * 1.204414 + xyz[2] * 0.045854;
    const bW = xyz[0] * -2079e-6 + xyz[1] * 0.048952 + xyz[2] * 0.953127;
    const f3 = 0.8 + surround / 10;
    const c2 = f3 >= 0.9 ? lerp(0.59, 0.69, (f3 - 0.9) * 10) : lerp(0.525, 0.59, (f3 - 0.8) * 10);
    let d = discountingIlluminant ? 1 : f3 * (1 - 1 / 3.6 * Math.exp((-adaptingLuminance - 42) / 92));
    d = d > 1 ? 1 : d < 0 ? 0 : d;
    const nc = f3;
    const rgbD = [
      d * (100 / rW) + 1 - d,
      d * (100 / gW) + 1 - d,
      d * (100 / bW) + 1 - d
    ];
    const k4 = 1 / (5 * adaptingLuminance + 1);
    const k42 = k4 * k4 * k4 * k4;
    const k4F = 1 - k42;
    const fl = k42 * adaptingLuminance + 0.1 * k4F * k4F * Math.cbrt(5 * adaptingLuminance);
    const n = yFromLstar(backgroundLstar) / whitePoint[1];
    const z = 1.48 + Math.sqrt(n);
    const nbb = 0.725 / Math.pow(n, 0.2);
    const ncb = nbb;
    const rgbAFactors = [
      Math.pow(fl * rgbD[0] * rW / 100, 0.42),
      Math.pow(fl * rgbD[1] * gW / 100, 0.42),
      Math.pow(fl * rgbD[2] * bW / 100, 0.42)
    ];
    const rgbA = [
      400 * rgbAFactors[0] / (rgbAFactors[0] + 27.13),
      400 * rgbAFactors[1] / (rgbAFactors[1] + 27.13),
      400 * rgbAFactors[2] / (rgbAFactors[2] + 27.13)
    ];
    const aw = (2 * rgbA[0] + rgbA[1] + 0.05 * rgbA[2]) * nbb;
    return new _ViewingConditions(n, aw, nbb, ncb, c2, nc, rgbD, fl, Math.pow(fl, 0.25), z);
  }
  /**
   * Parameters are intermediate values of the CAM16 conversion process. Their
   * names are shorthand for technical color science terminology, this class
   * would not benefit from documenting them individually. A brief overview
   * is available in the CAM16 specification, and a complete overview requires
   * a color science textbook, such as Fairchild's Color Appearance Models.
   */
  constructor(n, aw, nbb, ncb, c2, nc, rgbD, fl, fLRoot, z) {
    this.n = n;
    this.aw = aw;
    this.nbb = nbb;
    this.ncb = ncb;
    this.c = c2;
    this.nc = nc;
    this.rgbD = rgbD;
    this.fl = fl;
    this.fLRoot = fLRoot;
    this.z = z;
  }
};
ViewingConditions.DEFAULT = ViewingConditions.make();

// node_modules/@material/material-color-utilities/hct/cam16.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var Cam16 = class _Cam16 {
  /**
   * All of the CAM16 dimensions can be calculated from 3 of the dimensions, in
   * the following combinations:
   *      -  {j or q} and {c, m, or s} and hue
   *      - jstar, astar, bstar
   * Prefer using a static method that constructs from 3 of those dimensions.
   * This constructor is intended for those methods to use to return all
   * possible dimensions.
   *
   * @param hue
   * @param chroma informally, colorfulness / color intensity. like saturation
   *     in HSL, except perceptually accurate.
   * @param j lightness
   * @param q brightness; ratio of lightness to white point's lightness
   * @param m colorfulness
   * @param s saturation; ratio of chroma to white point's chroma
   * @param jstar CAM16-UCS J coordinate
   * @param astar CAM16-UCS a coordinate
   * @param bstar CAM16-UCS b coordinate
   */
  constructor(hue3, chroma, j, q, m, s, jstar, astar, bstar) {
    this.hue = hue3;
    this.chroma = chroma;
    this.j = j;
    this.q = q;
    this.m = m;
    this.s = s;
    this.jstar = jstar;
    this.astar = astar;
    this.bstar = bstar;
  }
  /**
   * CAM16 instances also have coordinates in the CAM16-UCS space, called J*,
   * a*, b*, or jstar, astar, bstar in code. CAM16-UCS is included in the CAM16
   * specification, and is used to measure distances between colors.
   */
  distance(other) {
    const dJ = this.jstar - other.jstar;
    const dA = this.astar - other.astar;
    const dB = this.bstar - other.bstar;
    const dEPrime = Math.sqrt(dJ * dJ + dA * dA + dB * dB);
    const dE = 1.41 * Math.pow(dEPrime, 0.63);
    return dE;
  }
  /**
   * @param argb ARGB representation of a color.
   * @return CAM16 color, assuming the color was viewed in default viewing
   *     conditions.
   */
  static fromInt(argb) {
    return _Cam16.fromIntInViewingConditions(argb, ViewingConditions.DEFAULT);
  }
  /**
   * @param argb ARGB representation of a color.
   * @param viewingConditions Information about the environment where the color
   *     was observed.
   * @return CAM16 color.
   */
  static fromIntInViewingConditions(argb, viewingConditions) {
    const red = (argb & 16711680) >> 16;
    const green = (argb & 65280) >> 8;
    const blue = argb & 255;
    const redL = linearized(red);
    const greenL = linearized(green);
    const blueL = linearized(blue);
    const x = 0.41233895 * redL + 0.35762064 * greenL + 0.18051042 * blueL;
    const y = 0.2126 * redL + 0.7152 * greenL + 0.0722 * blueL;
    const z = 0.01932141 * redL + 0.11916382 * greenL + 0.95034478 * blueL;
    const rC = 0.401288 * x + 0.650173 * y - 0.051461 * z;
    const gC = -0.250268 * x + 1.204414 * y + 0.045854 * z;
    const bC = -2079e-6 * x + 0.048952 * y + 0.953127 * z;
    const rD = viewingConditions.rgbD[0] * rC;
    const gD = viewingConditions.rgbD[1] * gC;
    const bD = viewingConditions.rgbD[2] * bC;
    const rAF = Math.pow(viewingConditions.fl * Math.abs(rD) / 100, 0.42);
    const gAF = Math.pow(viewingConditions.fl * Math.abs(gD) / 100, 0.42);
    const bAF = Math.pow(viewingConditions.fl * Math.abs(bD) / 100, 0.42);
    const rA = signum(rD) * 400 * rAF / (rAF + 27.13);
    const gA = signum(gD) * 400 * gAF / (gAF + 27.13);
    const bA = signum(bD) * 400 * bAF / (bAF + 27.13);
    const a = (11 * rA + -12 * gA + bA) / 11;
    const b = (rA + gA - 2 * bA) / 9;
    const u = (20 * rA + 20 * gA + 21 * bA) / 20;
    const p22 = (40 * rA + 20 * gA + bA) / 20;
    const atan2 = Math.atan2(b, a);
    const atanDegrees = atan2 * 180 / Math.PI;
    const hue3 = sanitizeDegreesDouble(atanDegrees);
    const hueRadians = hue3 * Math.PI / 180;
    const ac = p22 * viewingConditions.nbb;
    const j = 100 * Math.pow(ac / viewingConditions.aw, viewingConditions.c * viewingConditions.z);
    const q = 4 / viewingConditions.c * Math.sqrt(j / 100) * (viewingConditions.aw + 4) * viewingConditions.fLRoot;
    const huePrime = hue3 < 20.14 ? hue3 + 360 : hue3;
    const eHue = 0.25 * (Math.cos(huePrime * Math.PI / 180 + 2) + 3.8);
    const p1 = 5e4 / 13 * eHue * viewingConditions.nc * viewingConditions.ncb;
    const t = p1 * Math.sqrt(a * a + b * b) / (u + 0.305);
    const alpha = Math.pow(t, 0.9) * Math.pow(1.64 - Math.pow(0.29, viewingConditions.n), 0.73);
    const c2 = alpha * Math.sqrt(j / 100);
    const m = c2 * viewingConditions.fLRoot;
    const s = 50 * Math.sqrt(alpha * viewingConditions.c / (viewingConditions.aw + 4));
    const jstar = (1 + 100 * 7e-3) * j / (1 + 7e-3 * j);
    const mstar = 1 / 0.0228 * Math.log(1 + 0.0228 * m);
    const astar = mstar * Math.cos(hueRadians);
    const bstar = mstar * Math.sin(hueRadians);
    return new _Cam16(hue3, c2, j, q, m, s, jstar, astar, bstar);
  }
  /**
   * @param j CAM16 lightness
   * @param c CAM16 chroma
   * @param h CAM16 hue
   */
  static fromJch(j, c2, h) {
    return _Cam16.fromJchInViewingConditions(j, c2, h, ViewingConditions.DEFAULT);
  }
  /**
   * @param j CAM16 lightness
   * @param c CAM16 chroma
   * @param h CAM16 hue
   * @param viewingConditions Information about the environment where the color
   *     was observed.
   */
  static fromJchInViewingConditions(j, c2, h, viewingConditions) {
    const q = 4 / viewingConditions.c * Math.sqrt(j / 100) * (viewingConditions.aw + 4) * viewingConditions.fLRoot;
    const m = c2 * viewingConditions.fLRoot;
    const alpha = c2 / Math.sqrt(j / 100);
    const s = 50 * Math.sqrt(alpha * viewingConditions.c / (viewingConditions.aw + 4));
    const hueRadians = h * Math.PI / 180;
    const jstar = (1 + 100 * 7e-3) * j / (1 + 7e-3 * j);
    const mstar = 1 / 0.0228 * Math.log(1 + 0.0228 * m);
    const astar = mstar * Math.cos(hueRadians);
    const bstar = mstar * Math.sin(hueRadians);
    return new _Cam16(h, c2, j, q, m, s, jstar, astar, bstar);
  }
  /**
   * @param jstar CAM16-UCS lightness.
   * @param astar CAM16-UCS a dimension. Like a* in L*a*b*, it is a Cartesian
   *     coordinate on the Y axis.
   * @param bstar CAM16-UCS b dimension. Like a* in L*a*b*, it is a Cartesian
   *     coordinate on the X axis.
   */
  static fromUcs(jstar, astar, bstar) {
    return _Cam16.fromUcsInViewingConditions(jstar, astar, bstar, ViewingConditions.DEFAULT);
  }
  /**
   * @param jstar CAM16-UCS lightness.
   * @param astar CAM16-UCS a dimension. Like a* in L*a*b*, it is a Cartesian
   *     coordinate on the Y axis.
   * @param bstar CAM16-UCS b dimension. Like a* in L*a*b*, it is a Cartesian
   *     coordinate on the X axis.
   * @param viewingConditions Information about the environment where the color
   *     was observed.
   */
  static fromUcsInViewingConditions(jstar, astar, bstar, viewingConditions) {
    const a = astar;
    const b = bstar;
    const m = Math.sqrt(a * a + b * b);
    const M3 = (Math.exp(m * 0.0228) - 1) / 0.0228;
    const c2 = M3 / viewingConditions.fLRoot;
    let h = Math.atan2(b, a) * (180 / Math.PI);
    if (h < 0) {
      h += 360;
    }
    const j = jstar / (1 - (jstar - 100) * 7e-3);
    return _Cam16.fromJchInViewingConditions(j, c2, h, viewingConditions);
  }
  /**
   *  @return ARGB representation of color, assuming the color was viewed in
   *     default viewing conditions, which are near-identical to the default
   *     viewing conditions for sRGB.
   */
  toInt() {
    return this.viewed(ViewingConditions.DEFAULT);
  }
  /**
   * @param viewingConditions Information about the environment where the color
   *     will be viewed.
   * @return ARGB representation of color
   */
  viewed(viewingConditions) {
    const alpha = this.chroma === 0 || this.j === 0 ? 0 : this.chroma / Math.sqrt(this.j / 100);
    const t = Math.pow(alpha / Math.pow(1.64 - Math.pow(0.29, viewingConditions.n), 0.73), 1 / 0.9);
    const hRad = this.hue * Math.PI / 180;
    const eHue = 0.25 * (Math.cos(hRad + 2) + 3.8);
    const ac = viewingConditions.aw * Math.pow(this.j / 100, 1 / viewingConditions.c / viewingConditions.z);
    const p1 = eHue * (5e4 / 13) * viewingConditions.nc * viewingConditions.ncb;
    const p22 = ac / viewingConditions.nbb;
    const hSin = Math.sin(hRad);
    const hCos = Math.cos(hRad);
    const gamma4 = 23 * (p22 + 0.305) * t / (23 * p1 + 11 * t * hCos + 108 * t * hSin);
    const a = gamma4 * hCos;
    const b = gamma4 * hSin;
    const rA = (460 * p22 + 451 * a + 288 * b) / 1403;
    const gA = (460 * p22 - 891 * a - 261 * b) / 1403;
    const bA = (460 * p22 - 220 * a - 6300 * b) / 1403;
    const rCBase = Math.max(0, 27.13 * Math.abs(rA) / (400 - Math.abs(rA)));
    const rC = signum(rA) * (100 / viewingConditions.fl) * Math.pow(rCBase, 1 / 0.42);
    const gCBase = Math.max(0, 27.13 * Math.abs(gA) / (400 - Math.abs(gA)));
    const gC = signum(gA) * (100 / viewingConditions.fl) * Math.pow(gCBase, 1 / 0.42);
    const bCBase = Math.max(0, 27.13 * Math.abs(bA) / (400 - Math.abs(bA)));
    const bC = signum(bA) * (100 / viewingConditions.fl) * Math.pow(bCBase, 1 / 0.42);
    const rF = rC / viewingConditions.rgbD[0];
    const gF = gC / viewingConditions.rgbD[1];
    const bF = bC / viewingConditions.rgbD[2];
    const x = 1.86206786 * rF - 1.01125463 * gF + 0.14918677 * bF;
    const y = 0.38752654 * rF + 0.62144744 * gF - 897398e-8 * bF;
    const z = -0.0158415 * rF - 0.03412294 * gF + 1.04996444 * bF;
    const argb = argbFromXyz(x, y, z);
    return argb;
  }
  /// Given color expressed in XYZ and viewed in [viewingConditions], convert to
  /// CAM16.
  static fromXyzInViewingConditions(x, y, z, viewingConditions) {
    const rC = 0.401288 * x + 0.650173 * y - 0.051461 * z;
    const gC = -0.250268 * x + 1.204414 * y + 0.045854 * z;
    const bC = -2079e-6 * x + 0.048952 * y + 0.953127 * z;
    const rD = viewingConditions.rgbD[0] * rC;
    const gD = viewingConditions.rgbD[1] * gC;
    const bD = viewingConditions.rgbD[2] * bC;
    const rAF = Math.pow(viewingConditions.fl * Math.abs(rD) / 100, 0.42);
    const gAF = Math.pow(viewingConditions.fl * Math.abs(gD) / 100, 0.42);
    const bAF = Math.pow(viewingConditions.fl * Math.abs(bD) / 100, 0.42);
    const rA = signum(rD) * 400 * rAF / (rAF + 27.13);
    const gA = signum(gD) * 400 * gAF / (gAF + 27.13);
    const bA = signum(bD) * 400 * bAF / (bAF + 27.13);
    const a = (11 * rA + -12 * gA + bA) / 11;
    const b = (rA + gA - 2 * bA) / 9;
    const u = (20 * rA + 20 * gA + 21 * bA) / 20;
    const p22 = (40 * rA + 20 * gA + bA) / 20;
    const atan2 = Math.atan2(b, a);
    const atanDegrees = atan2 * 180 / Math.PI;
    const hue3 = atanDegrees < 0 ? atanDegrees + 360 : atanDegrees >= 360 ? atanDegrees - 360 : atanDegrees;
    const hueRadians = hue3 * Math.PI / 180;
    const ac = p22 * viewingConditions.nbb;
    const J = 100 * Math.pow(ac / viewingConditions.aw, viewingConditions.c * viewingConditions.z);
    const Q = 4 / viewingConditions.c * Math.sqrt(J / 100) * (viewingConditions.aw + 4) * viewingConditions.fLRoot;
    const huePrime = hue3 < 20.14 ? hue3 + 360 : hue3;
    const eHue = 1 / 4 * (Math.cos(huePrime * Math.PI / 180 + 2) + 3.8);
    const p1 = 5e4 / 13 * eHue * viewingConditions.nc * viewingConditions.ncb;
    const t = p1 * Math.sqrt(a * a + b * b) / (u + 0.305);
    const alpha = Math.pow(t, 0.9) * Math.pow(1.64 - Math.pow(0.29, viewingConditions.n), 0.73);
    const C = alpha * Math.sqrt(J / 100);
    const M3 = C * viewingConditions.fLRoot;
    const s = 50 * Math.sqrt(alpha * viewingConditions.c / (viewingConditions.aw + 4));
    const jstar = (1 + 100 * 7e-3) * J / (1 + 7e-3 * J);
    const mstar = Math.log(1 + 0.0228 * M3) / 0.0228;
    const astar = mstar * Math.cos(hueRadians);
    const bstar = mstar * Math.sin(hueRadians);
    return new _Cam16(hue3, C, J, Q, M3, s, jstar, astar, bstar);
  }
  /// XYZ representation of CAM16 seen in [viewingConditions].
  xyzInViewingConditions(viewingConditions) {
    const alpha = this.chroma === 0 || this.j === 0 ? 0 : this.chroma / Math.sqrt(this.j / 100);
    const t = Math.pow(alpha / Math.pow(1.64 - Math.pow(0.29, viewingConditions.n), 0.73), 1 / 0.9);
    const hRad = this.hue * Math.PI / 180;
    const eHue = 0.25 * (Math.cos(hRad + 2) + 3.8);
    const ac = viewingConditions.aw * Math.pow(this.j / 100, 1 / viewingConditions.c / viewingConditions.z);
    const p1 = eHue * (5e4 / 13) * viewingConditions.nc * viewingConditions.ncb;
    const p22 = ac / viewingConditions.nbb;
    const hSin = Math.sin(hRad);
    const hCos = Math.cos(hRad);
    const gamma4 = 23 * (p22 + 0.305) * t / (23 * p1 + 11 * t * hCos + 108 * t * hSin);
    const a = gamma4 * hCos;
    const b = gamma4 * hSin;
    const rA = (460 * p22 + 451 * a + 288 * b) / 1403;
    const gA = (460 * p22 - 891 * a - 261 * b) / 1403;
    const bA = (460 * p22 - 220 * a - 6300 * b) / 1403;
    const rCBase = Math.max(0, 27.13 * Math.abs(rA) / (400 - Math.abs(rA)));
    const rC = signum(rA) * (100 / viewingConditions.fl) * Math.pow(rCBase, 1 / 0.42);
    const gCBase = Math.max(0, 27.13 * Math.abs(gA) / (400 - Math.abs(gA)));
    const gC = signum(gA) * (100 / viewingConditions.fl) * Math.pow(gCBase, 1 / 0.42);
    const bCBase = Math.max(0, 27.13 * Math.abs(bA) / (400 - Math.abs(bA)));
    const bC = signum(bA) * (100 / viewingConditions.fl) * Math.pow(bCBase, 1 / 0.42);
    const rF = rC / viewingConditions.rgbD[0];
    const gF = gC / viewingConditions.rgbD[1];
    const bF = bC / viewingConditions.rgbD[2];
    const x = 1.86206786 * rF - 1.01125463 * gF + 0.14918677 * bF;
    const y = 0.38752654 * rF + 0.62144744 * gF - 897398e-8 * bF;
    const z = -0.0158415 * rF - 0.03412294 * gF + 1.04996444 * bF;
    return [x, y, z];
  }
};

// node_modules/@material/material-color-utilities/hct/hct_solver.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var HctSolver = class _HctSolver {
  /**
   * Sanitizes a small enough angle in radians.
   *
   * @param angle An angle in radians; must not deviate too much
   * from 0.
   * @return A coterminal angle between 0 and 2pi.
   */
  static sanitizeRadians(angle) {
    return (angle + Math.PI * 8) % (Math.PI * 2);
  }
  /**
   * Delinearizes an RGB component, returning a floating-point
   * number.
   *
   * @param rgbComponent 0.0 <= rgb_component <= 100.0, represents
   * linear R/G/B channel
   * @return 0.0 <= output <= 255.0, color channel converted to
   * regular RGB space
   */
  static trueDelinearized(rgbComponent) {
    const normalized = rgbComponent / 100;
    let delinearized2 = 0;
    if (normalized <= 31308e-7) {
      delinearized2 = normalized * 12.92;
    } else {
      delinearized2 = 1.055 * Math.pow(normalized, 1 / 2.4) - 0.055;
    }
    return delinearized2 * 255;
  }
  static chromaticAdaptation(component) {
    const af = Math.pow(Math.abs(component), 0.42);
    return signum(component) * 400 * af / (af + 27.13);
  }
  /**
   * Returns the hue of a linear RGB color in CAM16.
   *
   * @param linrgb The linear RGB coordinates of a color.
   * @return The hue of the color in CAM16, in radians.
   */
  static hueOf(linrgb) {
    const scaledDiscount = matrixMultiply(linrgb, _HctSolver.SCALED_DISCOUNT_FROM_LINRGB);
    const rA = _HctSolver.chromaticAdaptation(scaledDiscount[0]);
    const gA = _HctSolver.chromaticAdaptation(scaledDiscount[1]);
    const bA = _HctSolver.chromaticAdaptation(scaledDiscount[2]);
    const a = (11 * rA + -12 * gA + bA) / 11;
    const b = (rA + gA - 2 * bA) / 9;
    return Math.atan2(b, a);
  }
  static areInCyclicOrder(a, b, c2) {
    const deltaAB = _HctSolver.sanitizeRadians(b - a);
    const deltaAC = _HctSolver.sanitizeRadians(c2 - a);
    return deltaAB < deltaAC;
  }
  /**
   * Solves the lerp equation.
   *
   * @param source The starting number.
   * @param mid The number in the middle.
   * @param target The ending number.
   * @return A number t such that lerp(source, target, t) = mid.
   */
  static intercept(source, mid, target) {
    return (mid - source) / (target - source);
  }
  static lerpPoint(source, t, target) {
    return [
      source[0] + (target[0] - source[0]) * t,
      source[1] + (target[1] - source[1]) * t,
      source[2] + (target[2] - source[2]) * t
    ];
  }
  /**
   * Intersects a segment with a plane.
   *
   * @param source The coordinates of point A.
   * @param coordinate The R-, G-, or B-coordinate of the plane.
   * @param target The coordinates of point B.
   * @param axis The axis the plane is perpendicular with. (0: R, 1:
   * G, 2: B)
   * @return The intersection point of the segment AB with the plane
   * R=coordinate, G=coordinate, or B=coordinate
   */
  static setCoordinate(source, coordinate, target, axis) {
    const t = _HctSolver.intercept(source[axis], coordinate, target[axis]);
    return _HctSolver.lerpPoint(source, t, target);
  }
  static isBounded(x) {
    return 0 <= x && x <= 100;
  }
  /**
   * Returns the nth possible vertex of the polygonal intersection.
   *
   * @param y The Y value of the plane.
   * @param n The zero-based index of the point. 0 <= n <= 11.
   * @return The nth possible vertex of the polygonal intersection
   * of the y plane and the RGB cube, in linear RGB coordinates, if
   * it exists. If this possible vertex lies outside of the cube,
   * [-1.0, -1.0, -1.0] is returned.
   */
  static nthVertex(y, n) {
    const kR = _HctSolver.Y_FROM_LINRGB[0];
    const kG = _HctSolver.Y_FROM_LINRGB[1];
    const kB = _HctSolver.Y_FROM_LINRGB[2];
    const coordA = n % 4 <= 1 ? 0 : 100;
    const coordB = n % 2 === 0 ? 0 : 100;
    if (n < 4) {
      const g = coordA;
      const b = coordB;
      const r2 = (y - g * kG - b * kB) / kR;
      if (_HctSolver.isBounded(r2)) {
        return [r2, g, b];
      } else {
        return [-1, -1, -1];
      }
    } else if (n < 8) {
      const b = coordA;
      const r2 = coordB;
      const g = (y - r2 * kR - b * kB) / kG;
      if (_HctSolver.isBounded(g)) {
        return [r2, g, b];
      } else {
        return [-1, -1, -1];
      }
    } else {
      const r2 = coordA;
      const g = coordB;
      const b = (y - r2 * kR - g * kG) / kB;
      if (_HctSolver.isBounded(b)) {
        return [r2, g, b];
      } else {
        return [-1, -1, -1];
      }
    }
  }
  /**
   * Finds the segment containing the desired color.
   *
   * @param y The Y value of the color.
   * @param targetHue The hue of the color.
   * @return A list of two sets of linear RGB coordinates, each
   * corresponding to an endpoint of the segment containing the
   * desired color.
   */
  static bisectToSegment(y, targetHue) {
    let left = [-1, -1, -1];
    let right = left;
    let leftHue = 0;
    let rightHue = 0;
    let initialized = false;
    let uncut = true;
    for (let n = 0; n < 12; n++) {
      const mid = _HctSolver.nthVertex(y, n);
      if (mid[0] < 0) {
        continue;
      }
      const midHue = _HctSolver.hueOf(mid);
      if (!initialized) {
        left = mid;
        right = mid;
        leftHue = midHue;
        rightHue = midHue;
        initialized = true;
        continue;
      }
      if (uncut || _HctSolver.areInCyclicOrder(leftHue, midHue, rightHue)) {
        uncut = false;
        if (_HctSolver.areInCyclicOrder(leftHue, targetHue, midHue)) {
          right = mid;
          rightHue = midHue;
        } else {
          left = mid;
          leftHue = midHue;
        }
      }
    }
    return [left, right];
  }
  static midpoint(a, b) {
    return [
      (a[0] + b[0]) / 2,
      (a[1] + b[1]) / 2,
      (a[2] + b[2]) / 2
    ];
  }
  static criticalPlaneBelow(x) {
    return Math.floor(x - 0.5);
  }
  static criticalPlaneAbove(x) {
    return Math.ceil(x - 0.5);
  }
  /**
   * Finds a color with the given Y and hue on the boundary of the
   * cube.
   *
   * @param y The Y value of the color.
   * @param targetHue The hue of the color.
   * @return The desired color, in linear RGB coordinates.
   */
  static bisectToLimit(y, targetHue) {
    const segment = _HctSolver.bisectToSegment(y, targetHue);
    let left = segment[0];
    let leftHue = _HctSolver.hueOf(left);
    let right = segment[1];
    for (let axis = 0; axis < 3; axis++) {
      if (left[axis] !== right[axis]) {
        let lPlane = -1;
        let rPlane = 255;
        if (left[axis] < right[axis]) {
          lPlane = _HctSolver.criticalPlaneBelow(_HctSolver.trueDelinearized(left[axis]));
          rPlane = _HctSolver.criticalPlaneAbove(_HctSolver.trueDelinearized(right[axis]));
        } else {
          lPlane = _HctSolver.criticalPlaneAbove(_HctSolver.trueDelinearized(left[axis]));
          rPlane = _HctSolver.criticalPlaneBelow(_HctSolver.trueDelinearized(right[axis]));
        }
        for (let i = 0; i < 8; i++) {
          if (Math.abs(rPlane - lPlane) <= 1) {
            break;
          } else {
            const mPlane = Math.floor((lPlane + rPlane) / 2);
            const midPlaneCoordinate = _HctSolver.CRITICAL_PLANES[mPlane];
            const mid = _HctSolver.setCoordinate(left, midPlaneCoordinate, right, axis);
            const midHue = _HctSolver.hueOf(mid);
            if (_HctSolver.areInCyclicOrder(leftHue, targetHue, midHue)) {
              right = mid;
              rPlane = mPlane;
            } else {
              left = mid;
              leftHue = midHue;
              lPlane = mPlane;
            }
          }
        }
      }
    }
    return _HctSolver.midpoint(left, right);
  }
  static inverseChromaticAdaptation(adapted) {
    const adaptedAbs = Math.abs(adapted);
    const base = Math.max(0, 27.13 * adaptedAbs / (400 - adaptedAbs));
    return signum(adapted) * Math.pow(base, 1 / 0.42);
  }
  /**
   * Finds a color with the given hue, chroma, and Y.
   *
   * @param hueRadians The desired hue in radians.
   * @param chroma The desired chroma.
   * @param y The desired Y.
   * @return The desired color as a hexadecimal integer, if found; 0
   * otherwise.
   */
  static findResultByJ(hueRadians, chroma, y) {
    let j = Math.sqrt(y) * 11;
    const viewingConditions = ViewingConditions.DEFAULT;
    const tInnerCoeff = 1 / Math.pow(1.64 - Math.pow(0.29, viewingConditions.n), 0.73);
    const eHue = 0.25 * (Math.cos(hueRadians + 2) + 3.8);
    const p1 = eHue * (5e4 / 13) * viewingConditions.nc * viewingConditions.ncb;
    const hSin = Math.sin(hueRadians);
    const hCos = Math.cos(hueRadians);
    for (let iterationRound = 0; iterationRound < 5; iterationRound++) {
      const jNormalized = j / 100;
      const alpha = chroma === 0 || j === 0 ? 0 : chroma / Math.sqrt(jNormalized);
      const t = Math.pow(alpha * tInnerCoeff, 1 / 0.9);
      const ac = viewingConditions.aw * Math.pow(jNormalized, 1 / viewingConditions.c / viewingConditions.z);
      const p22 = ac / viewingConditions.nbb;
      const gamma4 = 23 * (p22 + 0.305) * t / (23 * p1 + 11 * t * hCos + 108 * t * hSin);
      const a = gamma4 * hCos;
      const b = gamma4 * hSin;
      const rA = (460 * p22 + 451 * a + 288 * b) / 1403;
      const gA = (460 * p22 - 891 * a - 261 * b) / 1403;
      const bA = (460 * p22 - 220 * a - 6300 * b) / 1403;
      const rCScaled = _HctSolver.inverseChromaticAdaptation(rA);
      const gCScaled = _HctSolver.inverseChromaticAdaptation(gA);
      const bCScaled = _HctSolver.inverseChromaticAdaptation(bA);
      const linrgb = matrixMultiply([rCScaled, gCScaled, bCScaled], _HctSolver.LINRGB_FROM_SCALED_DISCOUNT);
      if (linrgb[0] < 0 || linrgb[1] < 0 || linrgb[2] < 0) {
        return 0;
      }
      const kR = _HctSolver.Y_FROM_LINRGB[0];
      const kG = _HctSolver.Y_FROM_LINRGB[1];
      const kB = _HctSolver.Y_FROM_LINRGB[2];
      const fnj = kR * linrgb[0] + kG * linrgb[1] + kB * linrgb[2];
      if (fnj <= 0) {
        return 0;
      }
      if (iterationRound === 4 || Math.abs(fnj - y) < 2e-3) {
        if (linrgb[0] > 100.01 || linrgb[1] > 100.01 || linrgb[2] > 100.01) {
          return 0;
        }
        return argbFromLinrgb(linrgb);
      }
      j = j - (fnj - y) * j / (2 * fnj);
    }
    return 0;
  }
  /**
   * Finds an sRGB color with the given hue, chroma, and L*, if
   * possible.
   *
   * @param hueDegrees The desired hue, in degrees.
   * @param chroma The desired chroma.
   * @param lstar The desired L*.
   * @return A hexadecimal representing the sRGB color. The color
   * has sufficiently close hue, chroma, and L* to the desired
   * values, if possible; otherwise, the hue and L* will be
   * sufficiently close, and chroma will be maximized.
   */
  static solveToInt(hueDegrees, chroma, lstar) {
    if (chroma < 1e-4 || lstar < 1e-4 || lstar > 99.9999) {
      return argbFromLstar(lstar);
    }
    hueDegrees = sanitizeDegreesDouble(hueDegrees);
    const hueRadians = hueDegrees / 180 * Math.PI;
    const y = yFromLstar(lstar);
    const exactAnswer = _HctSolver.findResultByJ(hueRadians, chroma, y);
    if (exactAnswer !== 0) {
      return exactAnswer;
    }
    const linrgb = _HctSolver.bisectToLimit(y, hueRadians);
    return argbFromLinrgb(linrgb);
  }
  /**
   * Finds an sRGB color with the given hue, chroma, and L*, if
   * possible.
   *
   * @param hueDegrees The desired hue, in degrees.
   * @param chroma The desired chroma.
   * @param lstar The desired L*.
   * @return An CAM16 object representing the sRGB color. The color
   * has sufficiently close hue, chroma, and L* to the desired
   * values, if possible; otherwise, the hue and L* will be
   * sufficiently close, and chroma will be maximized.
   */
  static solveToCam(hueDegrees, chroma, lstar) {
    return Cam16.fromInt(_HctSolver.solveToInt(hueDegrees, chroma, lstar));
  }
};
HctSolver.SCALED_DISCOUNT_FROM_LINRGB = [
  [
    0.001200833568784504,
    0.002389694492170889,
    2795742885861124e-19
  ],
  [
    5891086651375999e-19,
    0.0029785502573438758,
    3270666104008398e-19
  ],
  [
    10146692491640572e-20,
    5364214359186694e-19,
    0.0032979401770712076
  ]
];
HctSolver.LINRGB_FROM_SCALED_DISCOUNT = [
  [
    1373.2198709594231,
    -1100.4251190754821,
    -7.278681089101213
  ],
  [
    -271.815969077903,
    559.6580465940733,
    -32.46047482791194
  ],
  [
    1.9622899599665666,
    -57.173814538844006,
    308.7233197812385
  ]
];
HctSolver.Y_FROM_LINRGB = [0.2126, 0.7152, 0.0722];
HctSolver.CRITICAL_PLANES = [
  0.015176349177441876,
  0.045529047532325624,
  0.07588174588720938,
  0.10623444424209313,
  0.13658714259697685,
  0.16693984095186062,
  0.19729253930674434,
  0.2276452376616281,
  0.2579979360165119,
  0.28835063437139563,
  0.3188300904430532,
  0.350925934958123,
  0.3848314933096426,
  0.42057480301049466,
  0.458183274052838,
  0.4976837250274023,
  0.5391024159806381,
  0.5824650784040898,
  0.6277969426914107,
  0.6751227633498623,
  0.7244668422128921,
  0.775853049866786,
  0.829304845476233,
  0.8848452951698498,
  0.942497089126609,
  1.0022825574869039,
  1.0642236851973577,
  1.1283421258858297,
  1.1946592148522128,
  1.2631959812511864,
  1.3339731595349034,
  1.407011200216447,
  1.4823302800086415,
  1.5599503113873272,
  1.6398909516233677,
  1.7221716113234105,
  1.8068114625156377,
  1.8938294463134073,
  1.9832442801866852,
  2.075074464868551,
  2.1693382909216234,
  2.2660538449872063,
  2.36523901573795,
  2.4669114995532007,
  2.5710888059345764,
  2.6777882626779785,
  2.7870270208169257,
  2.898822059350997,
  3.0131901897720907,
  3.1301480604002863,
  3.2497121605402226,
  3.3718988244681087,
  3.4967242352587946,
  3.624204428461639,
  3.754355295633311,
  3.887192587735158,
  4.022731918402185,
  4.160988767090289,
  4.301978482107941,
  4.445716283538092,
  4.592217266055746,
  4.741496401646282,
  4.893568542229298,
  5.048448422192488,
  5.20615066083972,
  5.3666897647573375,
  5.5300801301023865,
  5.696336044816294,
  5.865471690767354,
  6.037501145825082,
  6.212438385869475,
  6.390297286737924,
  6.571091626112461,
  6.7548350853498045,
  6.941541251256611,
  7.131223617812143,
  7.323895587840543,
  7.5195704746346665,
  7.7182615035334345,
  7.919981813454504,
  8.124744458384042,
  8.332562408825165,
  8.543448553206703,
  8.757415699253682,
  8.974476575321063,
  9.194643831691977,
  9.417930041841839,
  9.644347703669503,
  9.873909240696694,
  10.106627003236781,
  10.342513269534024,
  10.58158024687427,
  10.8238400726681,
  11.069304815507364,
  11.317986476196008,
  11.569896988756009,
  11.825048221409341,
  12.083451977536606,
  12.345119996613247,
  12.610063955123938,
  12.878295467455942,
  13.149826086772048,
  13.42466730586372,
  13.702830557985108,
  13.984327217668513,
  14.269168601521828,
  14.55736596900856,
  14.848930523210871,
  15.143873411576273,
  15.44220572664832,
  15.743938506781891,
  16.04908273684337,
  16.35764934889634,
  16.66964922287304,
  16.985093187232053,
  17.30399201960269,
  17.62635644741625,
  17.95219714852476,
  18.281524751807332,
  18.614349837764564,
  18.95068293910138,
  19.290534541298456,
  19.633915083172692,
  19.98083495742689,
  20.331304511189067,
  20.685334046541502,
  21.042933821039977,
  21.404114048223256,
  21.76888489811322,
  22.137256497705877,
  22.50923893145328,
  22.884842241736916,
  23.264076429332462,
  23.6469514538663,
  24.033477234264016,
  24.42366364919083,
  24.817520537484558,
  25.21505769858089,
  25.61628489293138,
  26.021211842414342,
  26.429848230738664,
  26.842203703840827,
  27.258287870275353,
  27.678110301598522,
  28.10168053274597,
  28.529008062403893,
  28.96010235337422,
  29.39497283293396,
  29.83362889318845,
  30.276079891419332,
  30.722335150426627,
  31.172403958865512,
  31.62629557157785,
  32.08401920991837,
  32.54558406207592,
  33.010999283389665,
  33.4802739966603,
  33.953417292456834,
  34.430438229418264,
  34.911345834551085,
  35.39614910352207,
  35.88485700094671,
  36.37747846067349,
  36.87402238606382,
  37.37449765026789,
  37.87891309649659,
  38.38727753828926,
  38.89959975977785,
  39.41588851594697,
  39.93615253289054,
  40.460400508064545,
  40.98864111053629,
  41.520882981230194,
  42.05713473317016,
  42.597404951718396,
  43.141702194811224,
  43.6900349931913,
  44.24241185063697,
  44.798841244188324,
  45.35933162437017,
  45.92389141541209,
  46.49252901546552,
  47.065252796817916,
  47.64207110610409,
  48.22299226451468,
  48.808024568002054,
  49.3971762874833,
  49.9904556690408,
  50.587870934119984,
  51.189430279724725,
  51.79514187861014,
  52.40501387947288,
  53.0190544071392,
  53.637271562750364,
  54.259673423945976,
  54.88626804504493,
  55.517063457223934,
  56.15206766869424,
  56.79128866487574,
  57.43473440856916,
  58.08241284012621,
  58.734331877617365,
  59.39049941699807,
  60.05092333227251,
  60.715611475655585,
  61.38457167773311,
  62.057811747619894,
  62.7353394731159,
  63.417162620860914,
  64.10328893648692,
  64.79372614476921,
  65.48848194977529,
  66.18756403501224,
  66.89098006357258,
  67.59873767827808,
  68.31084450182222,
  69.02730813691093,
  69.74813616640164,
  70.47333615344107,
  71.20291564160104,
  71.93688215501312,
  72.67524319850172,
  73.41800625771542,
  74.16517879925733,
  74.9167682708136,
  75.67278210128072,
  76.43322770089146,
  77.1981124613393,
  77.96744375590167,
  78.74122893956174,
  79.51947534912904,
  80.30219030335869,
  81.08938110306934,
  81.88105503125999,
  82.67721935322541,
  83.4778813166706,
  84.28304815182372,
  85.09272707154808,
  85.90692527145302,
  86.72564993000343,
  87.54890820862819,
  88.3767072518277,
  89.2090541872801,
  90.04595612594655,
  90.88742016217518,
  91.73345337380438,
  92.58406282226491,
  93.43925555268066,
  94.29903859396902,
  95.16341895893969,
  96.03240364439274,
  96.9059996312159,
  97.78421388448044,
  98.6670533535366,
  99.55452497210776
];

// node_modules/@material/material-color-utilities/hct/hct.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var Hct = class _Hct {
  static from(hue3, chroma, tone) {
    return new _Hct(HctSolver.solveToInt(hue3, chroma, tone));
  }
  /**
   * @param argb ARGB representation of a color.
   * @return HCT representation of a color in default viewing conditions
   */
  static fromInt(argb) {
    return new _Hct(argb);
  }
  toInt() {
    return this.argb;
  }
  /**
   * A number, in degrees, representing ex. red, orange, yellow, etc.
   * Ranges from 0 <= hue < 360.
   */
  get hue() {
    return this.internalHue;
  }
  /**
   * @param newHue 0 <= newHue < 360; invalid values are corrected.
   * Chroma may decrease because chroma has a different maximum for any given
   * hue and tone.
   */
  set hue(newHue) {
    this.setInternalState(HctSolver.solveToInt(newHue, this.internalChroma, this.internalTone));
  }
  get chroma() {
    return this.internalChroma;
  }
  /**
   * @param newChroma 0 <= newChroma < ?
   * Chroma may decrease because chroma has a different maximum for any given
   * hue and tone.
   */
  set chroma(newChroma) {
    this.setInternalState(HctSolver.solveToInt(this.internalHue, newChroma, this.internalTone));
  }
  /** Lightness. Ranges from 0 to 100. */
  get tone() {
    return this.internalTone;
  }
  /**
   * @param newTone 0 <= newTone <= 100; invalid valids are corrected.
   * Chroma may decrease because chroma has a different maximum for any given
   * hue and tone.
   */
  set tone(newTone) {
    this.setInternalState(HctSolver.solveToInt(this.internalHue, this.internalChroma, newTone));
  }
  /** Sets a property of the Hct object. */
  setValue(propertyName, value) {
    this[propertyName] = value;
  }
  toString() {
    return `HCT(${this.hue.toFixed(0)}, ${this.chroma.toFixed(0)}, ${this.tone.toFixed(0)})`;
  }
  static isBlue(hue3) {
    return hue3 >= 250 && hue3 < 270;
  }
  static isYellow(hue3) {
    return hue3 >= 105 && hue3 < 125;
  }
  static isCyan(hue3) {
    return hue3 >= 170 && hue3 < 207;
  }
  constructor(argb) {
    this.argb = argb;
    const cam = Cam16.fromInt(argb);
    this.internalHue = cam.hue;
    this.internalChroma = cam.chroma;
    this.internalTone = lstarFromArgb(argb);
    this.argb = argb;
  }
  setInternalState(argb) {
    const cam = Cam16.fromInt(argb);
    this.internalHue = cam.hue;
    this.internalChroma = cam.chroma;
    this.internalTone = lstarFromArgb(argb);
    this.argb = argb;
  }
  /**
   * Translates a color into different [ViewingConditions].
   *
   * Colors change appearance. They look different with lights on versus off,
   * the same color, as in hex code, on white looks different when on black.
   * This is called color relativity, most famously explicated by Josef Albers
   * in Interaction of Color.
   *
   * In color science, color appearance models can account for this and
   * calculate the appearance of a color in different settings. HCT is based on
   * CAM16, a color appearance model, and uses it to make these calculations.
   *
   * See [ViewingConditions.make] for parameters affecting color appearance.
   */
  inViewingConditions(vc) {
    const cam = Cam16.fromInt(this.toInt());
    const viewedInVc = cam.xyzInViewingConditions(vc);
    const recastInVc = Cam16.fromXyzInViewingConditions(viewedInVc[0], viewedInVc[1], viewedInVc[2], ViewingConditions.make());
    const recastHct = _Hct.from(recastInVc.hue, recastInVc.chroma, lstarFromY(viewedInVc[1]));
    return recastHct;
  }
};

// node_modules/@material/material-color-utilities/blend/blend.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var Blend = class _Blend {
  /**
   * Blend the design color's HCT hue towards the key color's HCT
   * hue, in a way that leaves the original color recognizable and
   * recognizably shifted towards the key color.
   *
   * @param designColor ARGB representation of an arbitrary color.
   * @param sourceColor ARGB representation of the main theme color.
   * @return The design color with a hue shifted towards the
   * system's color, a slightly warmer/cooler variant of the design
   * color's hue.
   */
  static harmonize(designColor, sourceColor) {
    const fromHct = Hct.fromInt(designColor);
    const toHct = Hct.fromInt(sourceColor);
    const differenceDegrees2 = differenceDegrees(fromHct.hue, toHct.hue);
    const rotationDegrees = Math.min(differenceDegrees2 * 0.5, 15);
    const outputHue = sanitizeDegreesDouble(fromHct.hue + rotationDegrees * rotationDirection(fromHct.hue, toHct.hue));
    return Hct.from(outputHue, fromHct.chroma, fromHct.tone).toInt();
  }
  /**
   * Blends hue from one color into another. The chroma and tone of
   * the original color are maintained.
   *
   * @param from ARGB representation of color
   * @param to ARGB representation of color
   * @param amount how much blending to perform; 0.0 >= and <= 1.0
   * @return from, with a hue blended towards to. Chroma and tone
   * are constant.
   */
  static hctHue(from, to, amount) {
    const ucs = _Blend.cam16Ucs(from, to, amount);
    const ucsCam = Cam16.fromInt(ucs);
    const fromCam = Cam16.fromInt(from);
    const blended = Hct.from(ucsCam.hue, fromCam.chroma, lstarFromArgb(from));
    return blended.toInt();
  }
  /**
   * Blend in CAM16-UCS space.
   *
   * @param from ARGB representation of color
   * @param to ARGB representation of color
   * @param amount how much blending to perform; 0.0 >= and <= 1.0
   * @return from, blended towards to. Hue, chroma, and tone will
   * change.
   */
  static cam16Ucs(from, to, amount) {
    const fromCam = Cam16.fromInt(from);
    const toCam = Cam16.fromInt(to);
    const fromJ = fromCam.jstar;
    const fromA = fromCam.astar;
    const fromB = fromCam.bstar;
    const toJ = toCam.jstar;
    const toA = toCam.astar;
    const toB = toCam.bstar;
    const jstar = fromJ + (toJ - fromJ) * amount;
    const astar = fromA + (toA - fromA) * amount;
    const bstar = fromB + (toB - fromB) * amount;
    return Cam16.fromUcs(jstar, astar, bstar).toInt();
  }
};

// node_modules/@material/material-color-utilities/contrast/contrast.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var Contrast = class _Contrast {
  /**
   * Returns a contrast ratio, which ranges from 1 to 21.
   *
   * @param toneA Tone between 0 and 100. Values outside will be clamped.
   * @param toneB Tone between 0 and 100. Values outside will be clamped.
   */
  static ratioOfTones(toneA, toneB) {
    toneA = clampDouble(0, 100, toneA);
    toneB = clampDouble(0, 100, toneB);
    return _Contrast.ratioOfYs(yFromLstar(toneA), yFromLstar(toneB));
  }
  static ratioOfYs(y1, y2) {
    const lighter = y1 > y2 ? y1 : y2;
    const darker = lighter === y2 ? y1 : y2;
    return (lighter + 5) / (darker + 5);
  }
  /**
   * Returns a tone >= tone parameter that ensures ratio parameter.
   * Return value is between 0 and 100.
   * Returns -1 if ratio cannot be achieved with tone parameter.
   *
   * @param tone Tone return value must contrast with.
   * Range is 0 to 100. Invalid values will result in -1 being returned.
   * @param ratio Contrast ratio of return value and tone.
   * Range is 1 to 21, invalid values have undefined behavior.
   */
  static lighter(tone, ratio) {
    if (tone < 0 || tone > 100) {
      return -1;
    }
    const darkY = yFromLstar(tone);
    const lightY = ratio * (darkY + 5) - 5;
    const realContrast = _Contrast.ratioOfYs(lightY, darkY);
    const delta = Math.abs(realContrast - ratio);
    if (realContrast < ratio && delta > 0.04) {
      return -1;
    }
    const returnValue = lstarFromY(lightY) + 0.4;
    if (returnValue < 0 || returnValue > 100) {
      return -1;
    }
    return returnValue;
  }
  /**
   * Returns a tone <= tone parameter that ensures ratio parameter.
   * Return value is between 0 and 100.
   * Returns -1 if ratio cannot be achieved with tone parameter.
   *
   * @param tone Tone return value must contrast with.
   * Range is 0 to 100. Invalid values will result in -1 being returned.
   * @param ratio Contrast ratio of return value and tone.
   * Range is 1 to 21, invalid values have undefined behavior.
   */
  static darker(tone, ratio) {
    if (tone < 0 || tone > 100) {
      return -1;
    }
    const lightY = yFromLstar(tone);
    const darkY = (lightY + 5) / ratio - 5;
    const realContrast = _Contrast.ratioOfYs(lightY, darkY);
    const delta = Math.abs(realContrast - ratio);
    if (realContrast < ratio && delta > 0.04) {
      return -1;
    }
    const returnValue = lstarFromY(darkY) - 0.4;
    if (returnValue < 0 || returnValue > 100) {
      return -1;
    }
    return returnValue;
  }
  /**
   * Returns a tone >= tone parameter that ensures ratio parameter.
   * Return value is between 0 and 100.
   * Returns 100 if ratio cannot be achieved with tone parameter.
   *
   * This method is unsafe because the returned value is guaranteed to be in
   * bounds for tone, i.e. between 0 and 100. However, that value may not reach
   * the ratio with tone. For example, there is no color lighter than T100.
   *
   * @param tone Tone return value must contrast with.
   * Range is 0 to 100. Invalid values will result in 100 being returned.
   * @param ratio Desired contrast ratio of return value and tone parameter.
   * Range is 1 to 21, invalid values have undefined behavior.
   */
  static lighterUnsafe(tone, ratio) {
    const lighterSafe = _Contrast.lighter(tone, ratio);
    return lighterSafe < 0 ? 100 : lighterSafe;
  }
  /**
   * Returns a tone >= tone parameter that ensures ratio parameter.
   * Return value is between 0 and 100.
   * Returns 100 if ratio cannot be achieved with tone parameter.
   *
   * This method is unsafe because the returned value is guaranteed to be in
   * bounds for tone, i.e. between 0 and 100. However, that value may not reach
   * the [ratio with [tone]. For example, there is no color darker than T0.
   *
   * @param tone Tone return value must contrast with.
   * Range is 0 to 100. Invalid values will result in 0 being returned.
   * @param ratio Desired contrast ratio of return value and tone parameter.
   * Range is 1 to 21, invalid values have undefined behavior.
   */
  static darkerUnsafe(tone, ratio) {
    const darkerSafe = _Contrast.darker(tone, ratio);
    return darkerSafe < 0 ? 0 : darkerSafe;
  }
};

// node_modules/@material/material-color-utilities/dislike/dislike_analyzer.js
/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var DislikeAnalyzer = class _DislikeAnalyzer {
  /**
   * Returns true if a color is disliked.
   *
   * @param hct A color to be judged.
   * @return Whether the color is disliked.
   *
   * Disliked is defined as a dark yellow-green that is not neutral.
   */
  static isDisliked(hct) {
    const huePasses = Math.round(hct.hue) >= 90 && Math.round(hct.hue) <= 111;
    const chromaPasses = Math.round(hct.chroma) > 16;
    const tonePasses = Math.round(hct.tone) < 65;
    return huePasses && chromaPasses && tonePasses;
  }
  /**
   * If a color is disliked, lighten it to make it likable.
   *
   * @param hct A color to be judged.
   * @return A new color if the original color is disliked, or the original
   *   color if it is acceptable.
   */
  static fixIfDisliked(hct) {
    if (_DislikeAnalyzer.isDisliked(hct)) {
      return Hct.from(hct.hue, hct.chroma, 70);
    }
    return hct;
  }
};

// node_modules/@material/material-color-utilities/dynamiccolor/dynamic_color.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
function validateExtendedColor(originalColor, specVersion, extendedColor) {
  if (originalColor.name !== extendedColor.name) {
    throw new Error(`Attempting to extend color ${originalColor.name} with color ${extendedColor.name} of different name for spec version ${specVersion}.`);
  }
  if (originalColor.isBackground !== extendedColor.isBackground) {
    throw new Error(`Attempting to extend color ${originalColor.name} as a ${originalColor.isBackground ? "background" : "foreground"} with color ${extendedColor.name} as a ${extendedColor.isBackground ? "background" : "foreground"} for spec version ${specVersion}.`);
  }
}
function extendSpecVersion(originlColor, specVersion, extendedColor) {
  validateExtendedColor(originlColor, specVersion, extendedColor);
  return DynamicColor.fromPalette({
    name: originlColor.name,
    palette: (s) => s.specVersion === specVersion ? extendedColor.palette(s) : originlColor.palette(s),
    tone: (s) => s.specVersion === specVersion ? extendedColor.tone(s) : originlColor.tone(s),
    isBackground: originlColor.isBackground,
    chromaMultiplier: (s) => {
      const chromaMultiplier = s.specVersion === specVersion ? extendedColor.chromaMultiplier : originlColor.chromaMultiplier;
      return chromaMultiplier !== void 0 ? chromaMultiplier(s) : 1;
    },
    background: (s) => {
      const background = s.specVersion === specVersion ? extendedColor.background : originlColor.background;
      return background !== void 0 ? background(s) : void 0;
    },
    secondBackground: (s) => {
      const secondBackground = s.specVersion === specVersion ? extendedColor.secondBackground : originlColor.secondBackground;
      return secondBackground !== void 0 ? secondBackground(s) : void 0;
    },
    contrastCurve: (s) => {
      const contrastCurve = s.specVersion === specVersion ? extendedColor.contrastCurve : originlColor.contrastCurve;
      return contrastCurve !== void 0 ? contrastCurve(s) : void 0;
    },
    toneDeltaPair: (s) => {
      const toneDeltaPair = s.specVersion === specVersion ? extendedColor.toneDeltaPair : originlColor.toneDeltaPair;
      return toneDeltaPair !== void 0 ? toneDeltaPair(s) : void 0;
    }
  });
}
var DynamicColor = class _DynamicColor {
  /**
   * Create a DynamicColor defined by a TonalPalette and HCT tone.
   *
   * @param args Functions with DynamicScheme as input. Must provide a palette
   *     and tone. May provide a background DynamicColor and ToneDeltaPair.
   */
  static fromPalette(args) {
    return new _DynamicColor(args.name ?? "", args.palette, args.tone ?? _DynamicColor.getInitialToneFromBackground(args.background), args.isBackground ?? false, args.chromaMultiplier, args.background, args.secondBackground, args.contrastCurve, args.toneDeltaPair);
  }
  static getInitialToneFromBackground(background) {
    if (background === void 0) {
      return (s) => 50;
    }
    return (s) => background(s) ? background(s).getTone(s) : 50;
  }
  /**
   * The base constructor for DynamicColor.
   *
   * _Strongly_ prefer using one of the convenience constructors. This class is
   * arguably too flexible to ensure it can support any scenario. Functional
   * arguments allow  overriding without risks that come with subclasses.
   *
   * For example, the default behavior of adjust tone at max contrast
   * to be at a 7.0 ratio with its background is principled and
   * matches accessibility guidance. That does not mean it's the desired
   * approach for _every_ design system, and every color pairing,
   * always, in every case.
   *
   * @param name The name of the dynamic color. Defaults to empty.
   * @param palette Function that provides a TonalPalette given DynamicScheme. A
   *     TonalPalette is defined by a hue and chroma, so this replaces the need
   *     to specify hue/chroma. By providing a tonal palette, when contrast
   *     adjustments are made, intended chroma can be preserved.
   * @param tone Function that provides a tone, given a DynamicScheme.
   * @param isBackground Whether this dynamic color is a background, with some
   *     other color as the foreground. Defaults to false.
   * @param chromaMultiplier A factor that multiplies the chroma for this color.
   * @param background The background of the dynamic color (as a function of a
   *     `DynamicScheme`), if it exists.
   * @param secondBackground A second background of the dynamic color (as a
   *     function of a `DynamicScheme`), if it exists.
   * @param contrastCurve A `ContrastCurve` object specifying how its contrast
   *     against its background should behave in various contrast levels
   *     options.
   * @param toneDeltaPair A `ToneDeltaPair` object specifying a tone delta
   *     constraint between two colors. One of them must be the color being
   *     constructed.
   */
  constructor(name, palette, tone, isBackground, chromaMultiplier, background, secondBackground, contrastCurve, toneDeltaPair) {
    this.name = name;
    this.palette = palette;
    this.tone = tone;
    this.isBackground = isBackground;
    this.chromaMultiplier = chromaMultiplier;
    this.background = background;
    this.secondBackground = secondBackground;
    this.contrastCurve = contrastCurve;
    this.toneDeltaPair = toneDeltaPair;
    this.hctCache = /* @__PURE__ */ new Map();
    if (!background && secondBackground) {
      throw new Error(`Color ${name} has secondBackgrounddefined, but background is not defined.`);
    }
    if (!background && contrastCurve) {
      throw new Error(`Color ${name} has contrastCurvedefined, but background is not defined.`);
    }
    if (background && !contrastCurve) {
      throw new Error(`Color ${name} has backgrounddefined, but contrastCurve is not defined.`);
    }
  }
  /**
   * Returns a deep copy of this DynamicColor.
   */
  clone() {
    return _DynamicColor.fromPalette({
      name: this.name,
      palette: this.palette,
      tone: this.tone,
      isBackground: this.isBackground,
      chromaMultiplier: this.chromaMultiplier,
      background: this.background,
      secondBackground: this.secondBackground,
      contrastCurve: this.contrastCurve,
      toneDeltaPair: this.toneDeltaPair
    });
  }
  /**
   * Clears the cache of HCT values for this color. For testing or debugging
   * purposes.
   */
  clearCache() {
    this.hctCache.clear();
  }
  /**
   * Returns a ARGB integer (i.e. a hex code).
   *
   * @param scheme Defines the conditions of the user interface, for example,
   *     whether or not it is dark mode or light mode, and what the desired
   *     contrast level is.
   */
  getArgb(scheme) {
    return this.getHct(scheme).toInt();
  }
  /**
   * Returns a color, expressed in the HCT color space, that this
   * DynamicColor is under the conditions in scheme.
   *
   * @param scheme Defines the conditions of the user interface, for example,
   *     whether or not it is dark mode or light mode, and what the desired
   *     contrast level is.
   */
  getHct(scheme) {
    const cachedAnswer = this.hctCache.get(scheme);
    if (cachedAnswer != null) {
      return cachedAnswer;
    }
    const answer = getSpec(scheme.specVersion).getHct(scheme, this);
    if (this.hctCache.size > 4) {
      this.hctCache.clear();
    }
    this.hctCache.set(scheme, answer);
    return answer;
  }
  /**
   * Returns a tone, T in the HCT color space, that this DynamicColor is under
   * the conditions in scheme.
   *
   * @param scheme Defines the conditions of the user interface, for example,
   *     whether or not it is dark mode or light mode, and what the desired
   *     contrast level is.
   */
  getTone(scheme) {
    return getSpec(scheme.specVersion).getTone(scheme, this);
  }
  /**
   * Given a background tone, finds a foreground tone, while ensuring they reach
   * a contrast ratio that is as close to [ratio] as possible.
   *
   * @param bgTone Tone in HCT. Range is 0 to 100, undefined behavior when it
   *     falls outside that range.
   * @param ratio The contrast ratio desired between bgTone and the return
   *     value.
   */
  static foregroundTone(bgTone, ratio) {
    const lighterTone = Contrast.lighterUnsafe(bgTone, ratio);
    const darkerTone = Contrast.darkerUnsafe(bgTone, ratio);
    const lighterRatio = Contrast.ratioOfTones(lighterTone, bgTone);
    const darkerRatio = Contrast.ratioOfTones(darkerTone, bgTone);
    const preferLighter = _DynamicColor.tonePrefersLightForeground(bgTone);
    if (preferLighter) {
      const negligibleDifference = Math.abs(lighterRatio - darkerRatio) < 0.1 && lighterRatio < ratio && darkerRatio < ratio;
      return lighterRatio >= ratio || lighterRatio >= darkerRatio || negligibleDifference ? lighterTone : darkerTone;
    } else {
      return darkerRatio >= ratio || darkerRatio >= lighterRatio ? darkerTone : lighterTone;
    }
  }
  /**
   * Returns whether [tone] prefers a light foreground.
   *
   * People prefer white foregrounds on ~T60-70. Observed over time, and also
   * by Andrew Somers during research for APCA.
   *
   * T60 used as to create the smallest discontinuity possible when skipping
   * down to T49 in order to ensure light foregrounds.
   * Since `tertiaryContainer` in dark monochrome scheme requires a tone of
   * 60, it should not be adjusted. Therefore, 60 is excluded here.
   */
  static tonePrefersLightForeground(tone) {
    return Math.round(tone) < 60;
  }
  /**
   * Returns whether [tone] can reach a contrast ratio of 4.5 with a lighter
   * color.
   */
  static toneAllowsLightForeground(tone) {
    return Math.round(tone) <= 49;
  }
  /**
   * Adjusts a tone such that white has 4.5 contrast, if the tone is
   * reasonably close to supporting it.
   */
  static enableLightForeground(tone) {
    if (_DynamicColor.tonePrefersLightForeground(tone) && !_DynamicColor.toneAllowsLightForeground(tone)) {
      return 49;
    }
    return tone;
  }
};
var ColorCalculationDelegateImpl2021 = class {
  getHct(scheme, color) {
    const tone = color.getTone(scheme);
    const palette = color.palette(scheme);
    return palette.getHct(tone);
  }
  getTone(scheme, color) {
    const decreasingContrast = scheme.contrastLevel < 0;
    const toneDeltaPair = color.toneDeltaPair ? color.toneDeltaPair(scheme) : void 0;
    if (toneDeltaPair) {
      const roleA = toneDeltaPair.roleA;
      const roleB = toneDeltaPair.roleB;
      const delta = toneDeltaPair.delta;
      const polarity = toneDeltaPair.polarity;
      const stayTogether = toneDeltaPair.stayTogether;
      const aIsNearer = polarity === "nearer" || polarity === "lighter" && !scheme.isDark || polarity === "darker" && scheme.isDark;
      const nearer = aIsNearer ? roleA : roleB;
      const farther = aIsNearer ? roleB : roleA;
      const amNearer = color.name === nearer.name;
      const expansionDir = scheme.isDark ? 1 : -1;
      let nTone = nearer.tone(scheme);
      let fTone = farther.tone(scheme);
      if (color.background && nearer.contrastCurve && farther.contrastCurve) {
        const bg = color.background(scheme);
        const nContrastCurve = nearer.contrastCurve(scheme);
        const fContrastCurve = farther.contrastCurve(scheme);
        if (bg && nContrastCurve && fContrastCurve) {
          const bgTone = bg.getTone(scheme);
          const nContrast = nContrastCurve.get(scheme.contrastLevel);
          const fContrast = fContrastCurve.get(scheme.contrastLevel);
          if (Contrast.ratioOfTones(bgTone, nTone) < nContrast) {
            nTone = DynamicColor.foregroundTone(bgTone, nContrast);
          }
          if (Contrast.ratioOfTones(bgTone, fTone) < fContrast) {
            fTone = DynamicColor.foregroundTone(bgTone, fContrast);
          }
          if (decreasingContrast) {
            nTone = DynamicColor.foregroundTone(bgTone, nContrast);
            fTone = DynamicColor.foregroundTone(bgTone, fContrast);
          }
        }
      }
      if ((fTone - nTone) * expansionDir < delta) {
        fTone = clampDouble(0, 100, nTone + delta * expansionDir);
        if ((fTone - nTone) * expansionDir >= delta) {
        } else {
          nTone = clampDouble(0, 100, fTone - delta * expansionDir);
        }
      }
      if (50 <= nTone && nTone < 60) {
        if (expansionDir > 0) {
          nTone = 60;
          fTone = Math.max(fTone, nTone + delta * expansionDir);
        } else {
          nTone = 49;
          fTone = Math.min(fTone, nTone + delta * expansionDir);
        }
      } else if (50 <= fTone && fTone < 60) {
        if (stayTogether) {
          if (expansionDir > 0) {
            nTone = 60;
            fTone = Math.max(fTone, nTone + delta * expansionDir);
          } else {
            nTone = 49;
            fTone = Math.min(fTone, nTone + delta * expansionDir);
          }
        } else {
          if (expansionDir > 0) {
            fTone = 60;
          } else {
            fTone = 49;
          }
        }
      }
      return amNearer ? nTone : fTone;
    } else {
      let answer = color.tone(scheme);
      if (color.background == void 0 || color.background(scheme) === void 0 || color.contrastCurve == void 0 || color.contrastCurve(scheme) === void 0) {
        return answer;
      }
      const bgTone = color.background(scheme).getTone(scheme);
      const desiredRatio = color.contrastCurve(scheme).get(scheme.contrastLevel);
      if (Contrast.ratioOfTones(bgTone, answer) >= desiredRatio) {
      } else {
        answer = DynamicColor.foregroundTone(bgTone, desiredRatio);
      }
      if (decreasingContrast) {
        answer = DynamicColor.foregroundTone(bgTone, desiredRatio);
      }
      if (color.isBackground && 50 <= answer && answer < 60) {
        if (Contrast.ratioOfTones(49, bgTone) >= desiredRatio) {
          answer = 49;
        } else {
          answer = 60;
        }
      }
      if (color.secondBackground == void 0 || color.secondBackground(scheme) === void 0) {
        return answer;
      }
      const [bg1, bg2] = [color.background, color.secondBackground];
      const [bgTone1, bgTone2] = [bg1(scheme).getTone(scheme), bg2(scheme).getTone(scheme)];
      const [upper, lower] = [Math.max(bgTone1, bgTone2), Math.min(bgTone1, bgTone2)];
      if (Contrast.ratioOfTones(upper, answer) >= desiredRatio && Contrast.ratioOfTones(lower, answer) >= desiredRatio) {
        return answer;
      }
      const lightOption = Contrast.lighter(upper, desiredRatio);
      const darkOption = Contrast.darker(lower, desiredRatio);
      const availables = [];
      if (lightOption !== -1)
        availables.push(lightOption);
      if (darkOption !== -1)
        availables.push(darkOption);
      const prefersLight = DynamicColor.tonePrefersLightForeground(bgTone1) || DynamicColor.tonePrefersLightForeground(bgTone2);
      if (prefersLight) {
        return lightOption < 0 ? 100 : lightOption;
      }
      if (availables.length === 1) {
        return availables[0];
      }
      return darkOption < 0 ? 0 : darkOption;
    }
  }
};
var ColorCalculationDelegateImpl2025 = class {
  getHct(scheme, color) {
    const palette = color.palette(scheme);
    const tone = color.getTone(scheme);
    const hue3 = palette.hue;
    const chroma = palette.chroma * (color.chromaMultiplier ? color.chromaMultiplier(scheme) : 1);
    return Hct.from(hue3, chroma, tone);
  }
  getTone(scheme, color) {
    const toneDeltaPair = color.toneDeltaPair ? color.toneDeltaPair(scheme) : void 0;
    if (toneDeltaPair) {
      const roleA = toneDeltaPair.roleA;
      const roleB = toneDeltaPair.roleB;
      const polarity = toneDeltaPair.polarity;
      const constraint = toneDeltaPair.constraint;
      const absoluteDelta = polarity === "darker" || polarity === "relative_lighter" && scheme.isDark || polarity === "relative_darker" && !scheme.isDark ? -toneDeltaPair.delta : toneDeltaPair.delta;
      const amRoleA = color.name === roleA.name;
      const selfRole = amRoleA ? roleA : roleB;
      const refRole = amRoleA ? roleB : roleA;
      let selfTone = selfRole.tone(scheme);
      let refTone = refRole.getTone(scheme);
      const relativeDelta = absoluteDelta * (amRoleA ? 1 : -1);
      if (constraint === "exact") {
        selfTone = clampDouble(0, 100, refTone + relativeDelta);
      } else if (constraint === "nearer") {
        if (relativeDelta > 0) {
          selfTone = clampDouble(0, 100, clampDouble(refTone, refTone + relativeDelta, selfTone));
        } else {
          selfTone = clampDouble(0, 100, clampDouble(refTone + relativeDelta, refTone, selfTone));
        }
      } else if (constraint === "farther") {
        if (relativeDelta > 0) {
          selfTone = clampDouble(refTone + relativeDelta, 100, selfTone);
        } else {
          selfTone = clampDouble(0, refTone + relativeDelta, selfTone);
        }
      }
      if (color.background && color.contrastCurve) {
        const background = color.background(scheme);
        const contrastCurve = color.contrastCurve(scheme);
        if (background && contrastCurve) {
          const bgTone = background.getTone(scheme);
          const selfContrast = contrastCurve.get(scheme.contrastLevel);
          selfTone = Contrast.ratioOfTones(bgTone, selfTone) >= selfContrast && scheme.contrastLevel >= 0 ? selfTone : DynamicColor.foregroundTone(bgTone, selfContrast);
        }
      }
      if (color.isBackground && !color.name.endsWith("_fixed_dim")) {
        if (selfTone >= 57) {
          selfTone = clampDouble(65, 100, selfTone);
        } else {
          selfTone = clampDouble(0, 49, selfTone);
        }
      }
      return selfTone;
    } else {
      let answer = color.tone(scheme);
      if (color.background == void 0 || color.background(scheme) === void 0 || color.contrastCurve == void 0 || color.contrastCurve(scheme) === void 0) {
        return answer;
      }
      const bgTone = color.background(scheme).getTone(scheme);
      const desiredRatio = color.contrastCurve(scheme).get(scheme.contrastLevel);
      answer = Contrast.ratioOfTones(bgTone, answer) >= desiredRatio && scheme.contrastLevel >= 0 ? answer : DynamicColor.foregroundTone(bgTone, desiredRatio);
      if (color.isBackground && !color.name.endsWith("_fixed_dim")) {
        if (answer >= 57) {
          answer = clampDouble(65, 100, answer);
        } else {
          answer = clampDouble(0, 49, answer);
        }
      }
      if (color.secondBackground == void 0 || color.secondBackground(scheme) === void 0) {
        return answer;
      }
      const [bg1, bg2] = [color.background, color.secondBackground];
      const [bgTone1, bgTone2] = [bg1(scheme).getTone(scheme), bg2(scheme).getTone(scheme)];
      const [upper, lower] = [Math.max(bgTone1, bgTone2), Math.min(bgTone1, bgTone2)];
      if (Contrast.ratioOfTones(upper, answer) >= desiredRatio && Contrast.ratioOfTones(lower, answer) >= desiredRatio) {
        return answer;
      }
      const lightOption = Contrast.lighter(upper, desiredRatio);
      const darkOption = Contrast.darker(lower, desiredRatio);
      const availables = [];
      if (lightOption !== -1)
        availables.push(lightOption);
      if (darkOption !== -1)
        availables.push(darkOption);
      const prefersLight = DynamicColor.tonePrefersLightForeground(bgTone1) || DynamicColor.tonePrefersLightForeground(bgTone2);
      if (prefersLight) {
        return lightOption < 0 ? 100 : lightOption;
      }
      if (availables.length === 1) {
        return availables[0];
      }
      return darkOption < 0 ? 0 : darkOption;
    }
  }
};
var spec2021 = new ColorCalculationDelegateImpl2021();
var spec2025 = new ColorCalculationDelegateImpl2025();
function getSpec(specVersion) {
  return specVersion === "2025" ? spec2025 : spec2021;
}

// node_modules/@material/material-color-utilities/palettes/tonal_palette.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var TonalPalette = class _TonalPalette {
  /**
   * @param argb ARGB representation of a color
   * @return Tones matching that color's hue and chroma.
   */
  static fromInt(argb) {
    const hct = Hct.fromInt(argb);
    return _TonalPalette.fromHct(hct);
  }
  /**
   * @param hct Hct
   * @return Tones matching that color's hue and chroma.
   */
  static fromHct(hct) {
    return new _TonalPalette(hct.hue, hct.chroma, hct);
  }
  /**
   * @param hue HCT hue
   * @param chroma HCT chroma
   * @return Tones matching hue and chroma.
   */
  static fromHueAndChroma(hue3, chroma) {
    const keyColor = new KeyColor(hue3, chroma).create();
    return new _TonalPalette(hue3, chroma, keyColor);
  }
  constructor(hue3, chroma, keyColor) {
    this.hue = hue3;
    this.chroma = chroma;
    this.keyColor = keyColor;
    this.cache = /* @__PURE__ */ new Map();
  }
  /**
   * @param tone HCT tone, measured from 0 to 100.
   * @return ARGB representation of a color with that tone.
   */
  tone(tone) {
    let argb = this.cache.get(tone);
    if (argb === void 0) {
      if (tone == 99 && Hct.isYellow(this.hue)) {
        argb = this.averageArgb(this.tone(98), this.tone(100));
      } else {
        argb = Hct.from(this.hue, this.chroma, tone).toInt();
      }
      this.cache.set(tone, argb);
    }
    return argb;
  }
  /**
   * @param tone HCT tone.
   * @return HCT representation of a color with that tone.
   */
  getHct(tone) {
    return Hct.fromInt(this.tone(tone));
  }
  averageArgb(argb1, argb2) {
    const red1 = argb1 >>> 16 & 255;
    const green1 = argb1 >>> 8 & 255;
    const blue1 = argb1 & 255;
    const red2 = argb2 >>> 16 & 255;
    const green2 = argb2 >>> 8 & 255;
    const blue2 = argb2 & 255;
    const red = Math.round((red1 + red2) / 2);
    const green = Math.round((green1 + green2) / 2);
    const blue = Math.round((blue1 + blue2) / 2);
    return (255 << 24 | (red & 255) << 16 | (green & 255) << 8 | blue & 255) >>> 0;
  }
};
var KeyColor = class {
  constructor(hue3, requestedChroma) {
    this.hue = hue3;
    this.requestedChroma = requestedChroma;
    this.chromaCache = /* @__PURE__ */ new Map();
    this.maxChromaValue = 200;
  }
  /**
   * Creates a key color from a [hue] and a [chroma].
   * The key color is the first tone, starting from T50, matching the given hue
   * and chroma.
   *
   * @return Key color [Hct]
   */
  create() {
    const pivotTone = 50;
    const toneStepSize = 1;
    const epsilon = 0.01;
    let lowerTone = 0;
    let upperTone = 100;
    while (lowerTone < upperTone) {
      const midTone = Math.floor((lowerTone + upperTone) / 2);
      const isAscending = this.maxChroma(midTone) < this.maxChroma(midTone + toneStepSize);
      const sufficientChroma = this.maxChroma(midTone) >= this.requestedChroma - epsilon;
      if (sufficientChroma) {
        if (Math.abs(lowerTone - pivotTone) < Math.abs(upperTone - pivotTone)) {
          upperTone = midTone;
        } else {
          if (lowerTone === midTone) {
            return Hct.from(this.hue, this.requestedChroma, lowerTone);
          }
          lowerTone = midTone;
        }
      } else {
        if (isAscending) {
          lowerTone = midTone + toneStepSize;
        } else {
          upperTone = midTone;
        }
      }
    }
    return Hct.from(this.hue, this.requestedChroma, lowerTone);
  }
  // Find the maximum chroma for a given tone
  maxChroma(tone) {
    if (this.chromaCache.has(tone)) {
      return this.chromaCache.get(tone);
    }
    const chroma = Hct.from(this.hue, this.maxChromaValue, tone).chroma;
    this.chromaCache.set(tone, chroma);
    return chroma;
  }
};

// node_modules/@material/material-color-utilities/temperature/temperature_cache.js
/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var TemperatureCache = class _TemperatureCache {
  constructor(input) {
    this.input = input;
    this.hctsByTempCache = [];
    this.hctsByHueCache = [];
    this.tempsByHctCache = /* @__PURE__ */ new Map();
    this.inputRelativeTemperatureCache = -1;
    this.complementCache = null;
  }
  get hctsByTemp() {
    if (this.hctsByTempCache.length > 0) {
      return this.hctsByTempCache;
    }
    const hcts = this.hctsByHue.concat([this.input]);
    const temperaturesByHct = this.tempsByHct;
    hcts.sort((a, b) => temperaturesByHct.get(a) - temperaturesByHct.get(b));
    this.hctsByTempCache = hcts;
    return hcts;
  }
  get warmest() {
    return this.hctsByTemp[this.hctsByTemp.length - 1];
  }
  get coldest() {
    return this.hctsByTemp[0];
  }
  /**
   * A set of colors with differing hues, equidistant in temperature.
   *
   * In art, this is usually described as a set of 5 colors on a color wheel
   * divided into 12 sections. This method allows provision of either of those
   * values.
   *
   * Behavior is undefined when [count] or [divisions] is 0.
   * When divisions < count, colors repeat.
   *
   * [count] The number of colors to return, includes the input color.
   * [divisions] The number of divisions on the color wheel.
   */
  analogous(count = 5, divisions = 12) {
    const startHue = Math.round(this.input.hue);
    const startHct = this.hctsByHue[startHue];
    let lastTemp = this.relativeTemperature(startHct);
    const allColors = [startHct];
    let absoluteTotalTempDelta = 0;
    for (let i = 0; i < 360; i++) {
      const hue3 = sanitizeDegreesInt(startHue + i);
      const hct = this.hctsByHue[hue3];
      const temp = this.relativeTemperature(hct);
      const tempDelta = Math.abs(temp - lastTemp);
      lastTemp = temp;
      absoluteTotalTempDelta += tempDelta;
    }
    let hueAddend = 1;
    const tempStep = absoluteTotalTempDelta / divisions;
    let totalTempDelta = 0;
    lastTemp = this.relativeTemperature(startHct);
    while (allColors.length < divisions) {
      const hue3 = sanitizeDegreesInt(startHue + hueAddend);
      const hct = this.hctsByHue[hue3];
      const temp = this.relativeTemperature(hct);
      const tempDelta = Math.abs(temp - lastTemp);
      totalTempDelta += tempDelta;
      const desiredTotalTempDeltaForIndex = allColors.length * tempStep;
      let indexSatisfied = totalTempDelta >= desiredTotalTempDeltaForIndex;
      let indexAddend = 1;
      while (indexSatisfied && allColors.length < divisions) {
        allColors.push(hct);
        const desiredTotalTempDeltaForIndex2 = (allColors.length + indexAddend) * tempStep;
        indexSatisfied = totalTempDelta >= desiredTotalTempDeltaForIndex2;
        indexAddend++;
      }
      lastTemp = temp;
      hueAddend++;
      if (hueAddend > 360) {
        while (allColors.length < divisions) {
          allColors.push(hct);
        }
        break;
      }
    }
    const answers = [this.input];
    const increaseHueCount = Math.floor((count - 1) / 2);
    for (let i = 1; i < increaseHueCount + 1; i++) {
      let index = 0 - i;
      while (index < 0) {
        index = allColors.length + index;
      }
      if (index >= allColors.length) {
        index = index % allColors.length;
      }
      answers.splice(0, 0, allColors[index]);
    }
    const decreaseHueCount = count - increaseHueCount - 1;
    for (let i = 1; i < decreaseHueCount + 1; i++) {
      let index = i;
      while (index < 0) {
        index = allColors.length + index;
      }
      if (index >= allColors.length) {
        index = index % allColors.length;
      }
      answers.push(allColors[index]);
    }
    return answers;
  }
  /**
   * A color that complements the input color aesthetically.
   *
   * In art, this is usually described as being across the color wheel.
   * History of this shows intent as a color that is just as cool-warm as the
   * input color is warm-cool.
   */
  get complement() {
    if (this.complementCache != null) {
      return this.complementCache;
    }
    const coldestHue = this.coldest.hue;
    const coldestTemp = this.tempsByHct.get(this.coldest);
    const warmestHue = this.warmest.hue;
    const warmestTemp = this.tempsByHct.get(this.warmest);
    const range = warmestTemp - coldestTemp;
    const startHueIsColdestToWarmest = _TemperatureCache.isBetween(this.input.hue, coldestHue, warmestHue);
    const startHue = startHueIsColdestToWarmest ? warmestHue : coldestHue;
    const endHue = startHueIsColdestToWarmest ? coldestHue : warmestHue;
    const directionOfRotation = 1;
    let smallestError = 1e3;
    let answer = this.hctsByHue[Math.round(this.input.hue)];
    const complementRelativeTemp = 1 - this.inputRelativeTemperature;
    for (let hueAddend = 0; hueAddend <= 360; hueAddend += 1) {
      const hue3 = sanitizeDegreesDouble(startHue + directionOfRotation * hueAddend);
      if (!_TemperatureCache.isBetween(hue3, startHue, endHue)) {
        continue;
      }
      const possibleAnswer = this.hctsByHue[Math.round(hue3)];
      const relativeTemp = (this.tempsByHct.get(possibleAnswer) - coldestTemp) / range;
      const error = Math.abs(complementRelativeTemp - relativeTemp);
      if (error < smallestError) {
        smallestError = error;
        answer = possibleAnswer;
      }
    }
    this.complementCache = answer;
    return this.complementCache;
  }
  /**
   * Temperature relative to all colors with the same chroma and tone.
   * Value on a scale from 0 to 1.
   */
  relativeTemperature(hct) {
    const range = this.tempsByHct.get(this.warmest) - this.tempsByHct.get(this.coldest);
    const differenceFromColdest = this.tempsByHct.get(hct) - this.tempsByHct.get(this.coldest);
    if (range === 0) {
      return 0.5;
    }
    return differenceFromColdest / range;
  }
  /** Relative temperature of the input color. See [relativeTemperature]. */
  get inputRelativeTemperature() {
    if (this.inputRelativeTemperatureCache >= 0) {
      return this.inputRelativeTemperatureCache;
    }
    this.inputRelativeTemperatureCache = this.relativeTemperature(this.input);
    return this.inputRelativeTemperatureCache;
  }
  /** A Map with keys of HCTs in [hctsByTemp], values of raw temperature. */
  get tempsByHct() {
    if (this.tempsByHctCache.size > 0) {
      return this.tempsByHctCache;
    }
    const allHcts = this.hctsByHue.concat([this.input]);
    const temperaturesByHct = /* @__PURE__ */ new Map();
    for (const e4 of allHcts) {
      temperaturesByHct.set(e4, _TemperatureCache.rawTemperature(e4));
    }
    this.tempsByHctCache = temperaturesByHct;
    return temperaturesByHct;
  }
  /**
   * HCTs for all hues, with the same chroma/tone as the input.
   * Sorted ascending, hue 0 to 360.
   */
  get hctsByHue() {
    if (this.hctsByHueCache.length > 0) {
      return this.hctsByHueCache;
    }
    const hcts = [];
    for (let hue3 = 0; hue3 <= 360; hue3 += 1) {
      const colorAtHue = Hct.from(hue3, this.input.chroma, this.input.tone);
      hcts.push(colorAtHue);
    }
    this.hctsByHueCache = hcts;
    return this.hctsByHueCache;
  }
  /** Determines if an angle is between two other angles, rotating clockwise. */
  static isBetween(angle, a, b) {
    if (a < b) {
      return a <= angle && angle <= b;
    }
    return a <= angle || angle <= b;
  }
  /**
   * Value representing cool-warm factor of a color.
   * Values below 0 are considered cool, above, warm.
   *
   * Color science has researched emotion and harmony, which art uses to select
   * colors. Warm-cool is the foundation of analogous and complementary colors.
   * See:
   * - Li-Chen Ou's Chapter 19 in Handbook of Color Psychology (2015).
   * - Josef Albers' Interaction of Color chapters 19 and 21.
   *
   * Implementation of Ou, Woodcock and Wright's algorithm, which uses
   * L*a*b* / LCH color space.
   * Return value has these properties:
   * - Values below 0 are cool, above 0 are warm.
   * - Lower bound: -0.52 - (chroma ^ 1.07 / 20). L*a*b* chroma is infinite.
   *   Assuming max of 130 chroma, -9.66.
   * - Upper bound: -0.52 + (chroma ^ 1.07 / 20). L*a*b* chroma is infinite.
   *   Assuming max of 130 chroma, 8.61.
   */
  static rawTemperature(color) {
    const lab2 = labFromArgb(color.toInt());
    const hue3 = sanitizeDegreesDouble(Math.atan2(lab2[2], lab2[1]) * 180 / Math.PI);
    const chroma = Math.sqrt(lab2[1] * lab2[1] + lab2[2] * lab2[2]);
    const temperature = -0.5 + 0.02 * Math.pow(chroma, 1.07) * Math.cos(sanitizeDegreesDouble(hue3 - 50) * Math.PI / 180);
    return temperature;
  }
};

// node_modules/@material/material-color-utilities/dynamiccolor/contrast_curve.js
/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var ContrastCurve = class {
  /**
   * Creates a `ContrastCurve` object.
   *
   * @param low Value for contrast level -1.0
   * @param normal Value for contrast level 0.0
   * @param medium Value for contrast level 0.5
   * @param high Value for contrast level 1.0
   */
  constructor(low, normal, medium, high) {
    this.low = low;
    this.normal = normal;
    this.medium = medium;
    this.high = high;
  }
  /**
   * Returns the value at a given contrast level.
   *
   * @param contrastLevel The contrast level. 0.0 is the default (normal); -1.0
   *     is the lowest; 1.0 is the highest.
   * @return The value. For contrast ratios, a number between 1.0 and 21.0.
   */
  get(contrastLevel) {
    if (contrastLevel <= -1) {
      return this.low;
    } else if (contrastLevel < 0) {
      return lerp(this.low, this.normal, (contrastLevel - -1) / 1);
    } else if (contrastLevel < 0.5) {
      return lerp(this.normal, this.medium, (contrastLevel - 0) / 0.5);
    } else if (contrastLevel < 1) {
      return lerp(this.medium, this.high, (contrastLevel - 0.5) / 0.5);
    } else {
      return this.high;
    }
  }
};

// node_modules/@material/material-color-utilities/dynamiccolor/tone_delta_pair.js
/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var ToneDeltaPair = class {
  /**
   * Documents a constraint in tone distance between two DynamicColors.
   *
   * The polarity is an adjective that describes "A", compared to "B".
   *
   * For instance, ToneDeltaPair(A, B, 15, 'darker', 'exact') states that
   * A's tone should be exactly 15 darker than B's.
   *
   * 'relative_darker' and 'relative_lighter' describes the tone adjustment
   * relative to the surface color trend (white in light mode; black in dark
   * mode). For instance, ToneDeltaPair(A, B, 10, 'relative_lighter',
   * 'farther') states that A should be at least 10 lighter than B in light
   * mode, and at least 10 darker than B in dark mode.
   *
   * @param roleA The first role in a pair.
   * @param roleB The second role in a pair.
   * @param delta Required difference between tones. Absolute value, negative
   * values have undefined behavior.
   * @param polarity The relative relation between tones of roleA and roleB,
   * as described above.
   * @param constraint How to fulfill the tone delta pair constraint.
   * @param stayTogether Whether these two roles should stay on the same side
   * of the "awkward zone" (T50-59). This is necessary for certain cases where
   * one role has two backgrounds.
   */
  constructor(roleA, roleB, delta, polarity, stayTogether, constraint) {
    this.roleA = roleA;
    this.roleB = roleB;
    this.delta = delta;
    this.polarity = polarity;
    this.stayTogether = stayTogether;
    this.constraint = constraint;
    this.constraint = constraint ?? "exact";
  }
};

// node_modules/@material/material-color-utilities/dynamiccolor/variant.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var Variant;
(function(Variant2) {
  Variant2[Variant2["MONOCHROME"] = 0] = "MONOCHROME";
  Variant2[Variant2["NEUTRAL"] = 1] = "NEUTRAL";
  Variant2[Variant2["TONAL_SPOT"] = 2] = "TONAL_SPOT";
  Variant2[Variant2["VIBRANT"] = 3] = "VIBRANT";
  Variant2[Variant2["EXPRESSIVE"] = 4] = "EXPRESSIVE";
  Variant2[Variant2["FIDELITY"] = 5] = "FIDELITY";
  Variant2[Variant2["CONTENT"] = 6] = "CONTENT";
  Variant2[Variant2["RAINBOW"] = 7] = "RAINBOW";
  Variant2[Variant2["FRUIT_SALAD"] = 8] = "FRUIT_SALAD";
})(Variant || (Variant = {}));

// node_modules/@material/material-color-utilities/dynamiccolor/color_spec_2021.js
/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
function isFidelity(scheme) {
  return scheme.variant === Variant.FIDELITY || scheme.variant === Variant.CONTENT;
}
function isMonochrome(scheme) {
  return scheme.variant === Variant.MONOCHROME;
}
function findDesiredChromaByTone(hue3, chroma, tone, byDecreasingTone) {
  let answer = tone;
  let closestToChroma = Hct.from(hue3, chroma, tone);
  if (closestToChroma.chroma < chroma) {
    let chromaPeak = closestToChroma.chroma;
    while (closestToChroma.chroma < chroma) {
      answer += byDecreasingTone ? -1 : 1;
      const potentialSolution = Hct.from(hue3, chroma, answer);
      if (chromaPeak > potentialSolution.chroma) {
        break;
      }
      if (Math.abs(potentialSolution.chroma - chroma) < 0.4) {
        break;
      }
      const potentialDelta = Math.abs(potentialSolution.chroma - chroma);
      const currentDelta = Math.abs(closestToChroma.chroma - chroma);
      if (potentialDelta < currentDelta) {
        closestToChroma = potentialSolution;
      }
      chromaPeak = Math.max(chromaPeak, potentialSolution.chroma);
    }
  }
  return answer;
}
var ColorSpecDelegateImpl2021 = class {
  ////////////////////////////////////////////////////////////////
  // Main Palettes                                              //
  ////////////////////////////////////////////////////////////////
  primaryPaletteKeyColor() {
    return DynamicColor.fromPalette({
      name: "primary_palette_key_color",
      palette: (s) => s.primaryPalette,
      tone: (s) => s.primaryPalette.keyColor.tone
    });
  }
  secondaryPaletteKeyColor() {
    return DynamicColor.fromPalette({
      name: "secondary_palette_key_color",
      palette: (s) => s.secondaryPalette,
      tone: (s) => s.secondaryPalette.keyColor.tone
    });
  }
  tertiaryPaletteKeyColor() {
    return DynamicColor.fromPalette({
      name: "tertiary_palette_key_color",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => s.tertiaryPalette.keyColor.tone
    });
  }
  neutralPaletteKeyColor() {
    return DynamicColor.fromPalette({
      name: "neutral_palette_key_color",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.neutralPalette.keyColor.tone
    });
  }
  neutralVariantPaletteKeyColor() {
    return DynamicColor.fromPalette({
      name: "neutral_variant_palette_key_color",
      palette: (s) => s.neutralVariantPalette,
      tone: (s) => s.neutralVariantPalette.keyColor.tone
    });
  }
  errorPaletteKeyColor() {
    return DynamicColor.fromPalette({
      name: "error_palette_key_color",
      palette: (s) => s.errorPalette,
      tone: (s) => s.errorPalette.keyColor.tone
    });
  }
  ////////////////////////////////////////////////////////////////
  // Surfaces [S]                                               //
  ////////////////////////////////////////////////////////////////
  background() {
    return DynamicColor.fromPalette({
      name: "background",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 6 : 98,
      isBackground: true
    });
  }
  onBackground() {
    return DynamicColor.fromPalette({
      name: "on_background",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 90 : 10,
      background: (s) => this.background(),
      contrastCurve: (s) => new ContrastCurve(3, 3, 4.5, 7)
    });
  }
  surface() {
    return DynamicColor.fromPalette({
      name: "surface",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 6 : 98,
      isBackground: true
    });
  }
  surfaceDim() {
    return DynamicColor.fromPalette({
      name: "surface_dim",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 6 : new ContrastCurve(87, 87, 80, 75).get(s.contrastLevel),
      isBackground: true
    });
  }
  surfaceBright() {
    return DynamicColor.fromPalette({
      name: "surface_bright",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? new ContrastCurve(24, 24, 29, 34).get(s.contrastLevel) : 98,
      isBackground: true
    });
  }
  surfaceContainerLowest() {
    return DynamicColor.fromPalette({
      name: "surface_container_lowest",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? new ContrastCurve(4, 4, 2, 0).get(s.contrastLevel) : 100,
      isBackground: true
    });
  }
  surfaceContainerLow() {
    return DynamicColor.fromPalette({
      name: "surface_container_low",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? new ContrastCurve(10, 10, 11, 12).get(s.contrastLevel) : new ContrastCurve(96, 96, 96, 95).get(s.contrastLevel),
      isBackground: true
    });
  }
  surfaceContainer() {
    return DynamicColor.fromPalette({
      name: "surface_container",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? new ContrastCurve(12, 12, 16, 20).get(s.contrastLevel) : new ContrastCurve(94, 94, 92, 90).get(s.contrastLevel),
      isBackground: true
    });
  }
  surfaceContainerHigh() {
    return DynamicColor.fromPalette({
      name: "surface_container_high",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? new ContrastCurve(17, 17, 21, 25).get(s.contrastLevel) : new ContrastCurve(92, 92, 88, 85).get(s.contrastLevel),
      isBackground: true
    });
  }
  surfaceContainerHighest() {
    return DynamicColor.fromPalette({
      name: "surface_container_highest",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? new ContrastCurve(22, 22, 26, 30).get(s.contrastLevel) : new ContrastCurve(90, 90, 84, 80).get(s.contrastLevel),
      isBackground: true
    });
  }
  onSurface() {
    return DynamicColor.fromPalette({
      name: "on_surface",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 90 : 10,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  surfaceVariant() {
    return DynamicColor.fromPalette({
      name: "surface_variant",
      palette: (s) => s.neutralVariantPalette,
      tone: (s) => s.isDark ? 30 : 90,
      isBackground: true
    });
  }
  onSurfaceVariant() {
    return DynamicColor.fromPalette({
      name: "on_surface_variant",
      palette: (s) => s.neutralVariantPalette,
      tone: (s) => s.isDark ? 80 : 30,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 11)
    });
  }
  inverseSurface() {
    return DynamicColor.fromPalette({
      name: "inverse_surface",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 90 : 20,
      isBackground: true
    });
  }
  inverseOnSurface() {
    return DynamicColor.fromPalette({
      name: "inverse_on_surface",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 20 : 95,
      background: (s) => this.inverseSurface(),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  outline() {
    return DynamicColor.fromPalette({
      name: "outline",
      palette: (s) => s.neutralVariantPalette,
      tone: (s) => s.isDark ? 60 : 50,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1.5, 3, 4.5, 7)
    });
  }
  outlineVariant() {
    return DynamicColor.fromPalette({
      name: "outline_variant",
      palette: (s) => s.neutralVariantPalette,
      tone: (s) => s.isDark ? 30 : 80,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5)
    });
  }
  shadow() {
    return DynamicColor.fromPalette({
      name: "shadow",
      palette: (s) => s.neutralPalette,
      tone: (s) => 0
    });
  }
  scrim() {
    return DynamicColor.fromPalette({
      name: "scrim",
      palette: (s) => s.neutralPalette,
      tone: (s) => 0
    });
  }
  surfaceTint() {
    return DynamicColor.fromPalette({
      name: "surface_tint",
      palette: (s) => s.primaryPalette,
      tone: (s) => s.isDark ? 80 : 40,
      isBackground: true
    });
  }
  ////////////////////////////////////////////////////////////////
  // Primary [P].                                               //
  ////////////////////////////////////////////////////////////////
  primary() {
    return DynamicColor.fromPalette({
      name: "primary",
      palette: (s) => s.primaryPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 100 : 0;
        }
        return s.isDark ? 80 : 40;
      },
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 7),
      toneDeltaPair: (s) => new ToneDeltaPair(this.primaryContainer(), this.primary(), 10, "nearer", false)
    });
  }
  primaryDim() {
    return void 0;
  }
  onPrimary() {
    return DynamicColor.fromPalette({
      name: "on_primary",
      palette: (s) => s.primaryPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 10 : 90;
        }
        return s.isDark ? 20 : 100;
      },
      background: (s) => this.primary(),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  primaryContainer() {
    return DynamicColor.fromPalette({
      name: "primary_container",
      palette: (s) => s.primaryPalette,
      tone: (s) => {
        if (isFidelity(s)) {
          return s.sourceColorHct.tone;
        }
        if (isMonochrome(s)) {
          return s.isDark ? 85 : 25;
        }
        return s.isDark ? 30 : 90;
      },
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.primaryContainer(), this.primary(), 10, "nearer", false)
    });
  }
  onPrimaryContainer() {
    return DynamicColor.fromPalette({
      name: "on_primary_container",
      palette: (s) => s.primaryPalette,
      tone: (s) => {
        if (isFidelity(s)) {
          return DynamicColor.foregroundTone(this.primaryContainer().tone(s), 4.5);
        }
        if (isMonochrome(s)) {
          return s.isDark ? 0 : 100;
        }
        return s.isDark ? 90 : 30;
      },
      background: (s) => this.primaryContainer(),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 11)
    });
  }
  inversePrimary() {
    return DynamicColor.fromPalette({
      name: "inverse_primary",
      palette: (s) => s.primaryPalette,
      tone: (s) => s.isDark ? 40 : 80,
      background: (s) => this.inverseSurface(),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 7)
    });
  }
  /////////////////////////////////////////////////////////////////
  // Secondary [Q].                                              //
  /////////////////////////////////////////////////////////////////
  secondary() {
    return DynamicColor.fromPalette({
      name: "secondary",
      palette: (s) => s.secondaryPalette,
      tone: (s) => s.isDark ? 80 : 40,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 7),
      toneDeltaPair: (s) => new ToneDeltaPair(this.secondaryContainer(), this.secondary(), 10, "nearer", false)
    });
  }
  secondaryDim() {
    return void 0;
  }
  onSecondary() {
    return DynamicColor.fromPalette({
      name: "on_secondary",
      palette: (s) => s.secondaryPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 10 : 100;
        } else {
          return s.isDark ? 20 : 100;
        }
      },
      background: (s) => this.secondary(),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  secondaryContainer() {
    return DynamicColor.fromPalette({
      name: "secondary_container",
      palette: (s) => s.secondaryPalette,
      tone: (s) => {
        const initialTone = s.isDark ? 30 : 90;
        if (isMonochrome(s)) {
          return s.isDark ? 30 : 85;
        }
        if (!isFidelity(s)) {
          return initialTone;
        }
        return findDesiredChromaByTone(s.secondaryPalette.hue, s.secondaryPalette.chroma, initialTone, s.isDark ? false : true);
      },
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.secondaryContainer(), this.secondary(), 10, "nearer", false)
    });
  }
  onSecondaryContainer() {
    return DynamicColor.fromPalette({
      name: "on_secondary_container",
      palette: (s) => s.secondaryPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 90 : 10;
        }
        if (!isFidelity(s)) {
          return s.isDark ? 90 : 30;
        }
        return DynamicColor.foregroundTone(this.secondaryContainer().tone(s), 4.5);
      },
      background: (s) => this.secondaryContainer(),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 11)
    });
  }
  /////////////////////////////////////////////////////////////////
  // Tertiary [T].                                               //
  /////////////////////////////////////////////////////////////////
  tertiary() {
    return DynamicColor.fromPalette({
      name: "tertiary",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 90 : 25;
        }
        return s.isDark ? 80 : 40;
      },
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 7),
      toneDeltaPair: (s) => new ToneDeltaPair(this.tertiaryContainer(), this.tertiary(), 10, "nearer", false)
    });
  }
  tertiaryDim() {
    return void 0;
  }
  onTertiary() {
    return DynamicColor.fromPalette({
      name: "on_tertiary",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 10 : 90;
        }
        return s.isDark ? 20 : 100;
      },
      background: (s) => this.tertiary(),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  tertiaryContainer() {
    return DynamicColor.fromPalette({
      name: "tertiary_container",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 60 : 49;
        }
        if (!isFidelity(s)) {
          return s.isDark ? 30 : 90;
        }
        const proposedHct = s.tertiaryPalette.getHct(s.sourceColorHct.tone);
        return DislikeAnalyzer.fixIfDisliked(proposedHct).tone;
      },
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.tertiaryContainer(), this.tertiary(), 10, "nearer", false)
    });
  }
  onTertiaryContainer() {
    return DynamicColor.fromPalette({
      name: "on_tertiary_container",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 0 : 100;
        }
        if (!isFidelity(s)) {
          return s.isDark ? 90 : 30;
        }
        return DynamicColor.foregroundTone(this.tertiaryContainer().tone(s), 4.5);
      },
      background: (s) => this.tertiaryContainer(),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 11)
    });
  }
  //////////////////////////////////////////////////////////////////
  // Error [E].                                                   //
  //////////////////////////////////////////////////////////////////
  error() {
    return DynamicColor.fromPalette({
      name: "error",
      palette: (s) => s.errorPalette,
      tone: (s) => s.isDark ? 80 : 40,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 7),
      toneDeltaPair: (s) => new ToneDeltaPair(this.errorContainer(), this.error(), 10, "nearer", false)
    });
  }
  errorDim() {
    return void 0;
  }
  onError() {
    return DynamicColor.fromPalette({
      name: "on_error",
      palette: (s) => s.errorPalette,
      tone: (s) => s.isDark ? 20 : 100,
      background: (s) => this.error(),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  errorContainer() {
    return DynamicColor.fromPalette({
      name: "error_container",
      palette: (s) => s.errorPalette,
      tone: (s) => s.isDark ? 30 : 90,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.errorContainer(), this.error(), 10, "nearer", false)
    });
  }
  onErrorContainer() {
    return DynamicColor.fromPalette({
      name: "on_error_container",
      palette: (s) => s.errorPalette,
      tone: (s) => {
        if (isMonochrome(s)) {
          return s.isDark ? 90 : 10;
        }
        return s.isDark ? 90 : 30;
      },
      background: (s) => this.errorContainer(),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 11)
    });
  }
  //////////////////////////////////////////////////////////////////
  // Primary Fixed [PF]                                           //
  //////////////////////////////////////////////////////////////////
  primaryFixed() {
    return DynamicColor.fromPalette({
      name: "primary_fixed",
      palette: (s) => s.primaryPalette,
      tone: (s) => isMonochrome(s) ? 40 : 90,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.primaryFixed(), this.primaryFixedDim(), 10, "lighter", true)
    });
  }
  primaryFixedDim() {
    return DynamicColor.fromPalette({
      name: "primary_fixed_dim",
      palette: (s) => s.primaryPalette,
      tone: (s) => isMonochrome(s) ? 30 : 80,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.primaryFixed(), this.primaryFixedDim(), 10, "lighter", true)
    });
  }
  onPrimaryFixed() {
    return DynamicColor.fromPalette({
      name: "on_primary_fixed",
      palette: (s) => s.primaryPalette,
      tone: (s) => isMonochrome(s) ? 100 : 10,
      background: (s) => this.primaryFixedDim(),
      secondBackground: (s) => this.primaryFixed(),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  onPrimaryFixedVariant() {
    return DynamicColor.fromPalette({
      name: "on_primary_fixed_variant",
      palette: (s) => s.primaryPalette,
      tone: (s) => isMonochrome(s) ? 90 : 30,
      background: (s) => this.primaryFixedDim(),
      secondBackground: (s) => this.primaryFixed(),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 11)
    });
  }
  ///////////////////////////////////////////////////////////////////
  // Secondary Fixed [QF]                                          //
  ///////////////////////////////////////////////////////////////////
  secondaryFixed() {
    return DynamicColor.fromPalette({
      name: "secondary_fixed",
      palette: (s) => s.secondaryPalette,
      tone: (s) => isMonochrome(s) ? 80 : 90,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.secondaryFixed(), this.secondaryFixedDim(), 10, "lighter", true)
    });
  }
  secondaryFixedDim() {
    return DynamicColor.fromPalette({
      name: "secondary_fixed_dim",
      palette: (s) => s.secondaryPalette,
      tone: (s) => isMonochrome(s) ? 70 : 80,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.secondaryFixed(), this.secondaryFixedDim(), 10, "lighter", true)
    });
  }
  onSecondaryFixed() {
    return DynamicColor.fromPalette({
      name: "on_secondary_fixed",
      palette: (s) => s.secondaryPalette,
      tone: (s) => 10,
      background: (s) => this.secondaryFixedDim(),
      secondBackground: (s) => this.secondaryFixed(),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  onSecondaryFixedVariant() {
    return DynamicColor.fromPalette({
      name: "on_secondary_fixed_variant",
      palette: (s) => s.secondaryPalette,
      tone: (s) => isMonochrome(s) ? 25 : 30,
      background: (s) => this.secondaryFixedDim(),
      secondBackground: (s) => this.secondaryFixed(),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 11)
    });
  }
  /////////////////////////////////////////////////////////////////
  // Tertiary Fixed [TF]                                         //
  /////////////////////////////////////////////////////////////////
  tertiaryFixed() {
    return DynamicColor.fromPalette({
      name: "tertiary_fixed",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => isMonochrome(s) ? 40 : 90,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.tertiaryFixed(), this.tertiaryFixedDim(), 10, "lighter", true)
    });
  }
  tertiaryFixedDim() {
    return DynamicColor.fromPalette({
      name: "tertiary_fixed_dim",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => isMonochrome(s) ? 30 : 80,
      isBackground: true,
      background: (s) => this.highestSurface(s),
      contrastCurve: (s) => new ContrastCurve(1, 1, 3, 4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.tertiaryFixed(), this.tertiaryFixedDim(), 10, "lighter", true)
    });
  }
  onTertiaryFixed() {
    return DynamicColor.fromPalette({
      name: "on_tertiary_fixed",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => isMonochrome(s) ? 100 : 10,
      background: (s) => this.tertiaryFixedDim(),
      secondBackground: (s) => this.tertiaryFixed(),
      contrastCurve: (s) => new ContrastCurve(4.5, 7, 11, 21)
    });
  }
  onTertiaryFixedVariant() {
    return DynamicColor.fromPalette({
      name: "on_tertiary_fixed_variant",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => isMonochrome(s) ? 90 : 30,
      background: (s) => this.tertiaryFixedDim(),
      secondBackground: (s) => this.tertiaryFixed(),
      contrastCurve: (s) => new ContrastCurve(3, 4.5, 7, 11)
    });
  }
  ////////////////////////////////////////////////////////////////
  // Other                                                      //
  ////////////////////////////////////////////////////////////////
  highestSurface(s) {
    return s.isDark ? this.surfaceBright() : this.surfaceDim();
  }
};

// node_modules/@material/material-color-utilities/dynamiccolor/color_spec_2025.js
/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
function tMaxC(palette, lowerBound = 0, upperBound = 100, chromaMultiplier = 1) {
  let answer = findBestToneForChroma(palette.hue, palette.chroma * chromaMultiplier, 100, true);
  return clampDouble(lowerBound, upperBound, answer);
}
function tMinC(palette, lowerBound = 0, upperBound = 100) {
  let answer = findBestToneForChroma(palette.hue, palette.chroma, 0, false);
  return clampDouble(lowerBound, upperBound, answer);
}
function findBestToneForChroma(hue3, chroma, tone, byDecreasingTone) {
  let answer = tone;
  let bestCandidate = Hct.from(hue3, chroma, answer);
  while (bestCandidate.chroma < chroma) {
    if (tone < 0 || tone > 100) {
      break;
    }
    tone += byDecreasingTone ? -1 : 1;
    const newCandidate = Hct.from(hue3, chroma, tone);
    if (bestCandidate.chroma < newCandidate.chroma) {
      bestCandidate = newCandidate;
      answer = tone;
    }
  }
  return answer;
}
function getCurve(defaultContrast) {
  if (defaultContrast === 1.5) {
    return new ContrastCurve(1.5, 1.5, 3, 5.5);
  } else if (defaultContrast === 3) {
    return new ContrastCurve(3, 3, 4.5, 7);
  } else if (defaultContrast === 4.5) {
    return new ContrastCurve(4.5, 4.5, 7, 11);
  } else if (defaultContrast === 6) {
    return new ContrastCurve(6, 6, 7, 11);
  } else if (defaultContrast === 7) {
    return new ContrastCurve(7, 7, 11, 21);
  } else if (defaultContrast === 9) {
    return new ContrastCurve(9, 9, 11, 21);
  } else if (defaultContrast === 11) {
    return new ContrastCurve(11, 11, 21, 21);
  } else if (defaultContrast === 21) {
    return new ContrastCurve(21, 21, 21, 21);
  } else {
    return new ContrastCurve(defaultContrast, defaultContrast, 7, 21);
  }
}
var ColorSpecDelegateImpl2025 = class extends ColorSpecDelegateImpl2021 {
  ////////////////////////////////////////////////////////////////
  // Surfaces [S]                                               //
  ////////////////////////////////////////////////////////////////
  surface() {
    const color2025 = DynamicColor.fromPalette({
      name: "surface",
      palette: (s) => s.neutralPalette,
      tone: (s) => {
        super.surface().tone(s);
        if (s.platform === "phone") {
          if (s.isDark) {
            return 4;
          } else {
            if (Hct.isYellow(s.neutralPalette.hue)) {
              return 99;
            } else if (s.variant === Variant.VIBRANT) {
              return 97;
            } else {
              return 98;
            }
          }
        } else {
          return 0;
        }
      },
      isBackground: true
    });
    return extendSpecVersion(super.surface(), "2025", color2025);
  }
  surfaceDim() {
    const color2025 = DynamicColor.fromPalette({
      name: "surface_dim",
      palette: (s) => s.neutralPalette,
      tone: (s) => {
        if (s.isDark) {
          return 4;
        } else {
          if (Hct.isYellow(s.neutralPalette.hue)) {
            return 90;
          } else if (s.variant === Variant.VIBRANT) {
            return 85;
          } else {
            return 87;
          }
        }
      },
      isBackground: true,
      chromaMultiplier: (s) => {
        if (!s.isDark) {
          if (s.variant === Variant.NEUTRAL) {
            return 2.5;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.7;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? 2.7 : 1.75;
          } else if (s.variant === Variant.VIBRANT) {
            return 1.36;
          }
        }
        return 1;
      }
    });
    return extendSpecVersion(super.surfaceDim(), "2025", color2025);
  }
  surfaceBright() {
    const color2025 = DynamicColor.fromPalette({
      name: "surface_bright",
      palette: (s) => s.neutralPalette,
      tone: (s) => {
        if (s.isDark) {
          return 18;
        } else {
          if (Hct.isYellow(s.neutralPalette.hue)) {
            return 99;
          } else if (s.variant === Variant.VIBRANT) {
            return 97;
          } else {
            return 98;
          }
        }
      },
      isBackground: true,
      chromaMultiplier: (s) => {
        if (s.isDark) {
          if (s.variant === Variant.NEUTRAL) {
            return 2.5;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.7;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? 2.7 : 1.75;
          } else if (s.variant === Variant.VIBRANT) {
            return 1.36;
          }
        }
        return 1;
      }
    });
    return extendSpecVersion(super.surfaceBright(), "2025", color2025);
  }
  surfaceContainerLowest() {
    const color2025 = DynamicColor.fromPalette({
      name: "surface_container_lowest",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 0 : 100,
      isBackground: true
    });
    return extendSpecVersion(super.surfaceContainerLowest(), "2025", color2025);
  }
  surfaceContainerLow() {
    const color2025 = DynamicColor.fromPalette({
      name: "surface_container_low",
      palette: (s) => s.neutralPalette,
      tone: (s) => {
        if (s.platform === "phone") {
          if (s.isDark) {
            return 6;
          } else {
            if (Hct.isYellow(s.neutralPalette.hue)) {
              return 98;
            } else if (s.variant === Variant.VIBRANT) {
              return 95;
            } else {
              return 96;
            }
          }
        } else {
          return 15;
        }
      },
      isBackground: true,
      chromaMultiplier: (s) => {
        if (s.platform === "phone") {
          if (s.variant === Variant.NEUTRAL) {
            return 1.3;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.25;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? 1.3 : 1.15;
          } else if (s.variant === Variant.VIBRANT) {
            return 1.08;
          }
        }
        return 1;
      }
    });
    return extendSpecVersion(super.surfaceContainerLow(), "2025", color2025);
  }
  surfaceContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "surface_container",
      palette: (s) => s.neutralPalette,
      tone: (s) => {
        if (s.platform === "phone") {
          if (s.isDark) {
            return 9;
          } else {
            if (Hct.isYellow(s.neutralPalette.hue)) {
              return 96;
            } else if (s.variant === Variant.VIBRANT) {
              return 92;
            } else {
              return 94;
            }
          }
        } else {
          return 20;
        }
      },
      isBackground: true,
      chromaMultiplier: (s) => {
        if (s.platform === "phone") {
          if (s.variant === Variant.NEUTRAL) {
            return 1.6;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.4;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? 1.6 : 1.3;
          } else if (s.variant === Variant.VIBRANT) {
            return 1.15;
          }
        }
        return 1;
      }
    });
    return extendSpecVersion(super.surfaceContainer(), "2025", color2025);
  }
  surfaceContainerHigh() {
    const color2025 = DynamicColor.fromPalette({
      name: "surface_container_high",
      palette: (s) => s.neutralPalette,
      tone: (s) => {
        if (s.platform === "phone") {
          if (s.isDark) {
            return 12;
          } else {
            if (Hct.isYellow(s.neutralPalette.hue)) {
              return 94;
            } else if (s.variant === Variant.VIBRANT) {
              return 90;
            } else {
              return 92;
            }
          }
        } else {
          return 25;
        }
      },
      isBackground: true,
      chromaMultiplier: (s) => {
        if (s.platform === "phone") {
          if (s.variant === Variant.NEUTRAL) {
            return 1.9;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.5;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? 1.95 : 1.45;
          } else if (s.variant === Variant.VIBRANT) {
            return 1.22;
          }
        }
        return 1;
      }
    });
    return extendSpecVersion(super.surfaceContainerHigh(), "2025", color2025);
  }
  surfaceContainerHighest() {
    const color2025 = DynamicColor.fromPalette({
      name: "surface_container_highest",
      palette: (s) => s.neutralPalette,
      tone: (s) => {
        if (s.isDark) {
          return 15;
        } else {
          if (Hct.isYellow(s.neutralPalette.hue)) {
            return 92;
          } else if (s.variant === Variant.VIBRANT) {
            return 88;
          } else {
            return 90;
          }
        }
      },
      isBackground: true,
      chromaMultiplier: (s) => {
        if (s.variant === Variant.NEUTRAL) {
          return 2.2;
        } else if (s.variant === Variant.TONAL_SPOT) {
          return 1.7;
        } else if (s.variant === Variant.EXPRESSIVE) {
          return Hct.isYellow(s.neutralPalette.hue) ? 2.3 : 1.6;
        } else if (s.variant === Variant.VIBRANT) {
          return 1.29;
        } else {
          return 1;
        }
      }
    });
    return extendSpecVersion(super.surfaceContainerHighest(), "2025", color2025);
  }
  onSurface() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_surface",
      palette: (s) => s.neutralPalette,
      tone: (s) => {
        if (s.variant === Variant.VIBRANT) {
          return tMaxC(s.neutralPalette, 0, 100, 1.1);
        } else {
          return DynamicColor.getInitialToneFromBackground((s2) => s2.platform === "phone" ? this.highestSurface(s2) : this.surfaceContainerHigh())(s);
        }
      },
      chromaMultiplier: (s) => {
        if (s.platform === "phone") {
          if (s.variant === Variant.NEUTRAL) {
            return 2.2;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.7;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? s.isDark ? 3 : 2.3 : 1.6;
          }
        }
        return 1;
      },
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : this.surfaceContainerHigh(),
      contrastCurve: (s) => s.isDark && s.platform === "phone" ? getCurve(11) : getCurve(9)
    });
    return extendSpecVersion(super.onSurface(), "2025", color2025);
  }
  onSurfaceVariant() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_surface_variant",
      palette: (s) => s.neutralPalette,
      chromaMultiplier: (s) => {
        if (s.platform === "phone") {
          if (s.variant === Variant.NEUTRAL) {
            return 2.2;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.7;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? s.isDark ? 3 : 2.3 : 1.6;
          }
        }
        return 1;
      },
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : this.surfaceContainerHigh(),
      contrastCurve: (s) => s.platform === "phone" ? s.isDark ? getCurve(6) : getCurve(4.5) : getCurve(7)
    });
    return extendSpecVersion(super.onSurfaceVariant(), "2025", color2025);
  }
  outline() {
    const color2025 = DynamicColor.fromPalette({
      name: "outline",
      palette: (s) => s.neutralPalette,
      chromaMultiplier: (s) => {
        if (s.platform === "phone") {
          if (s.variant === Variant.NEUTRAL) {
            return 2.2;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.7;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? s.isDark ? 3 : 2.3 : 1.6;
          }
        }
        return 1;
      },
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : this.surfaceContainerHigh(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(3) : getCurve(4.5)
    });
    return extendSpecVersion(super.outline(), "2025", color2025);
  }
  outlineVariant() {
    const color2025 = DynamicColor.fromPalette({
      name: "outline_variant",
      palette: (s) => s.neutralPalette,
      chromaMultiplier: (s) => {
        if (s.platform === "phone") {
          if (s.variant === Variant.NEUTRAL) {
            return 2.2;
          } else if (s.variant === Variant.TONAL_SPOT) {
            return 1.7;
          } else if (s.variant === Variant.EXPRESSIVE) {
            return Hct.isYellow(s.neutralPalette.hue) ? s.isDark ? 3 : 2.3 : 1.6;
          }
        }
        return 1;
      },
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : this.surfaceContainerHigh(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(1.5) : getCurve(3)
    });
    return extendSpecVersion(super.outlineVariant(), "2025", color2025);
  }
  inverseSurface() {
    const color2025 = DynamicColor.fromPalette({
      name: "inverse_surface",
      palette: (s) => s.neutralPalette,
      tone: (s) => s.isDark ? 98 : 4,
      isBackground: true
    });
    return extendSpecVersion(super.inverseSurface(), "2025", color2025);
  }
  inverseOnSurface() {
    const color2025 = DynamicColor.fromPalette({
      name: "inverse_on_surface",
      palette: (s) => s.neutralPalette,
      background: (s) => this.inverseSurface(),
      contrastCurve: (s) => getCurve(7)
    });
    return extendSpecVersion(super.inverseOnSurface(), "2025", color2025);
  }
  ////////////////////////////////////////////////////////////////
  // Primaries [P]                                              //
  ////////////////////////////////////////////////////////////////
  primary() {
    const color2025 = DynamicColor.fromPalette({
      name: "primary",
      palette: (s) => s.primaryPalette,
      tone: (s) => {
        if (s.variant === Variant.NEUTRAL) {
          if (s.platform === "phone") {
            return s.isDark ? 80 : 40;
          } else {
            return 90;
          }
        } else if (s.variant === Variant.TONAL_SPOT) {
          if (s.platform === "phone") {
            if (s.isDark) {
              return 80;
            } else {
              return tMaxC(s.primaryPalette);
            }
          } else {
            return tMaxC(s.primaryPalette, 0, 90);
          }
        } else if (s.variant === Variant.EXPRESSIVE) {
          if (s.platform === "phone") {
            return tMaxC(s.primaryPalette, 0, Hct.isYellow(s.primaryPalette.hue) ? 25 : Hct.isCyan(s.primaryPalette.hue) ? 88 : 98);
          } else {
            return tMaxC(s.primaryPalette);
          }
        } else {
          if (s.platform === "phone") {
            return tMaxC(s.primaryPalette, 0, Hct.isCyan(s.primaryPalette.hue) ? 88 : 98);
          } else {
            return tMaxC(s.primaryPalette);
          }
        }
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : this.surfaceContainerHigh(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(4.5) : getCurve(7),
      toneDeltaPair: (s) => s.platform === "phone" ? new ToneDeltaPair(this.primaryContainer(), this.primary(), 5, "relative_lighter", true, "farther") : void 0
    });
    return extendSpecVersion(super.primary(), "2025", color2025);
  }
  primaryDim() {
    return DynamicColor.fromPalette({
      name: "primary_dim",
      palette: (s) => s.primaryPalette,
      tone: (s) => {
        if (s.variant === Variant.NEUTRAL) {
          return 85;
        } else if (s.variant === Variant.TONAL_SPOT) {
          return tMaxC(s.primaryPalette, 0, 90);
        } else {
          return tMaxC(s.primaryPalette);
        }
      },
      isBackground: true,
      background: (s) => this.surfaceContainerHigh(),
      contrastCurve: (s) => getCurve(4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.primaryDim(), this.primary(), 5, "darker", true, "farther")
    });
  }
  onPrimary() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_primary",
      palette: (s) => s.primaryPalette,
      background: (s) => s.platform === "phone" ? this.primary() : this.primaryDim(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(6) : getCurve(7)
    });
    return extendSpecVersion(super.onPrimary(), "2025", color2025);
  }
  primaryContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "primary_container",
      palette: (s) => s.primaryPalette,
      tone: (s) => {
        if (s.platform === "watch") {
          return 30;
        } else if (s.variant === Variant.NEUTRAL) {
          return s.isDark ? 30 : 90;
        } else if (s.variant === Variant.TONAL_SPOT) {
          return s.isDark ? tMinC(s.primaryPalette, 35, 93) : tMaxC(s.primaryPalette, 0, 90);
        } else if (s.variant === Variant.EXPRESSIVE) {
          return s.isDark ? tMaxC(s.primaryPalette, 30, 93) : tMaxC(s.primaryPalette, 78, Hct.isCyan(s.primaryPalette.hue) ? 88 : 90);
        } else {
          return s.isDark ? tMinC(s.primaryPalette, 66, 93) : tMaxC(s.primaryPalette, 66, Hct.isCyan(s.primaryPalette.hue) ? 88 : 93);
        }
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : void 0,
      toneDeltaPair: (s) => s.platform === "phone" ? void 0 : new ToneDeltaPair(this.primaryContainer(), this.primaryDim(), 10, "darker", true, "farther"),
      contrastCurve: (s) => s.platform === "phone" && s.contrastLevel > 0 ? getCurve(1.5) : void 0
    });
    return extendSpecVersion(super.primaryContainer(), "2025", color2025);
  }
  onPrimaryContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_primary_container",
      palette: (s) => s.primaryPalette,
      background: (s) => this.primaryContainer(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(6) : getCurve(7)
    });
    return extendSpecVersion(super.onPrimaryContainer(), "2025", color2025);
  }
  primaryFixed() {
    const color2025 = DynamicColor.fromPalette({
      name: "primary_fixed",
      palette: (s) => s.primaryPalette,
      tone: (s) => {
        let tempS = Object.assign({}, s, { isDark: false, contrastLevel: 0 });
        return this.primaryContainer().getTone(tempS);
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : void 0,
      contrastCurve: (s) => s.platform === "phone" && s.contrastLevel > 0 ? getCurve(1.5) : void 0
    });
    return extendSpecVersion(super.primaryFixed(), "2025", color2025);
  }
  primaryFixedDim() {
    const color2025 = DynamicColor.fromPalette({
      name: "primary_fixed_dim",
      palette: (s) => s.primaryPalette,
      tone: (s) => this.primaryFixed().getTone(s),
      isBackground: true,
      toneDeltaPair: (s) => new ToneDeltaPair(this.primaryFixedDim(), this.primaryFixed(), 5, "darker", true, "exact")
    });
    return extendSpecVersion(super.primaryFixedDim(), "2025", color2025);
  }
  onPrimaryFixed() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_primary_fixed",
      palette: (s) => s.primaryPalette,
      background: (s) => this.primaryFixedDim(),
      contrastCurve: (s) => getCurve(7)
    });
    return extendSpecVersion(super.onPrimaryFixed(), "2025", color2025);
  }
  onPrimaryFixedVariant() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_primary_fixed_variant",
      palette: (s) => s.primaryPalette,
      background: (s) => this.primaryFixedDim(),
      contrastCurve: (s) => getCurve(4.5)
    });
    return extendSpecVersion(super.onPrimaryFixedVariant(), "2025", color2025);
  }
  inversePrimary() {
    const color2025 = DynamicColor.fromPalette({
      name: "inverse_primary",
      palette: (s) => s.primaryPalette,
      tone: (s) => tMaxC(s.primaryPalette),
      background: (s) => this.inverseSurface(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(6) : getCurve(7)
    });
    return extendSpecVersion(super.inversePrimary(), "2025", color2025);
  }
  ////////////////////////////////////////////////////////////////
  // Secondaries [Q]                                            //
  ////////////////////////////////////////////////////////////////
  secondary() {
    const color2025 = DynamicColor.fromPalette({
      name: "secondary",
      palette: (s) => s.secondaryPalette,
      tone: (s) => {
        if (s.platform === "watch") {
          return s.variant === Variant.NEUTRAL ? 90 : tMaxC(s.secondaryPalette, 0, 90);
        } else if (s.variant === Variant.NEUTRAL) {
          return s.isDark ? tMinC(s.secondaryPalette, 0, 98) : tMaxC(s.secondaryPalette);
        } else if (s.variant === Variant.VIBRANT) {
          return tMaxC(s.secondaryPalette, 0, s.isDark ? 90 : 98);
        } else {
          return s.isDark ? 80 : tMaxC(s.secondaryPalette);
        }
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : this.surfaceContainerHigh(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(4.5) : getCurve(7),
      toneDeltaPair: (s) => s.platform === "phone" ? new ToneDeltaPair(this.secondaryContainer(), this.secondary(), 5, "relative_lighter", true, "farther") : void 0
    });
    return extendSpecVersion(super.secondary(), "2025", color2025);
  }
  secondaryDim() {
    return DynamicColor.fromPalette({
      name: "secondary_dim",
      palette: (s) => s.secondaryPalette,
      tone: (s) => {
        if (s.variant === Variant.NEUTRAL) {
          return 85;
        } else {
          return tMaxC(s.secondaryPalette, 0, 90);
        }
      },
      isBackground: true,
      background: (s) => this.surfaceContainerHigh(),
      contrastCurve: (s) => getCurve(4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.secondaryDim(), this.secondary(), 5, "darker", true, "farther")
    });
  }
  onSecondary() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_secondary",
      palette: (s) => s.secondaryPalette,
      background: (s) => s.platform === "phone" ? this.secondary() : this.secondaryDim(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(6) : getCurve(7)
    });
    return extendSpecVersion(super.onSecondary(), "2025", color2025);
  }
  secondaryContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "secondary_container",
      palette: (s) => s.secondaryPalette,
      tone: (s) => {
        if (s.platform === "watch") {
          return 30;
        } else if (s.variant === Variant.VIBRANT) {
          return s.isDark ? tMinC(s.secondaryPalette, 30, 40) : tMaxC(s.secondaryPalette, 84, 90);
        } else if (s.variant === Variant.EXPRESSIVE) {
          return s.isDark ? 15 : tMaxC(s.secondaryPalette, 90, 95);
        } else {
          return s.isDark ? 25 : 90;
        }
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : void 0,
      toneDeltaPair: (s) => s.platform === "watch" ? new ToneDeltaPair(this.secondaryContainer(), this.secondaryDim(), 10, "darker", true, "farther") : void 0,
      contrastCurve: (s) => s.platform === "phone" && s.contrastLevel > 0 ? getCurve(1.5) : void 0
    });
    return extendSpecVersion(super.secondaryContainer(), "2025", color2025);
  }
  onSecondaryContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_secondary_container",
      palette: (s) => s.secondaryPalette,
      background: (s) => this.secondaryContainer(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(6) : getCurve(7)
    });
    return extendSpecVersion(super.onSecondaryContainer(), "2025", color2025);
  }
  secondaryFixed() {
    const color2025 = DynamicColor.fromPalette({
      name: "secondary_fixed",
      palette: (s) => s.secondaryPalette,
      tone: (s) => {
        let tempS = Object.assign({}, s, { isDark: false, contrastLevel: 0 });
        return this.secondaryContainer().getTone(tempS);
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : void 0,
      contrastCurve: (s) => s.platform === "phone" && s.contrastLevel > 0 ? getCurve(1.5) : void 0
    });
    return extendSpecVersion(super.secondaryFixed(), "2025", color2025);
  }
  secondaryFixedDim() {
    const color2025 = DynamicColor.fromPalette({
      name: "secondary_fixed_dim",
      palette: (s) => s.secondaryPalette,
      tone: (s) => this.secondaryFixed().getTone(s),
      isBackground: true,
      toneDeltaPair: (s) => new ToneDeltaPair(this.secondaryFixedDim(), this.secondaryFixed(), 5, "darker", true, "exact")
    });
    return extendSpecVersion(super.secondaryFixedDim(), "2025", color2025);
  }
  onSecondaryFixed() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_secondary_fixed",
      palette: (s) => s.secondaryPalette,
      background: (s) => this.secondaryFixedDim(),
      contrastCurve: (s) => getCurve(7)
    });
    return extendSpecVersion(super.onSecondaryFixed(), "2025", color2025);
  }
  onSecondaryFixedVariant() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_secondary_fixed_variant",
      palette: (s) => s.secondaryPalette,
      background: (s) => this.secondaryFixedDim(),
      contrastCurve: (s) => getCurve(4.5)
    });
    return extendSpecVersion(super.onSecondaryFixedVariant(), "2025", color2025);
  }
  ////////////////////////////////////////////////////////////////
  // Tertiaries [T]                                             //
  ////////////////////////////////////////////////////////////////
  tertiary() {
    const color2025 = DynamicColor.fromPalette({
      name: "tertiary",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => {
        if (s.platform === "watch") {
          return s.variant === Variant.TONAL_SPOT ? tMaxC(s.tertiaryPalette, 0, 90) : tMaxC(s.tertiaryPalette);
        } else if (s.variant === Variant.EXPRESSIVE || s.variant === Variant.VIBRANT) {
          return tMaxC(s.tertiaryPalette, 0, Hct.isCyan(s.tertiaryPalette.hue) ? 88 : s.isDark ? 98 : 100);
        } else {
          return s.isDark ? tMaxC(s.tertiaryPalette, 0, 98) : tMaxC(s.tertiaryPalette);
        }
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : this.surfaceContainerHigh(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(4.5) : getCurve(7),
      toneDeltaPair: (s) => s.platform === "phone" ? new ToneDeltaPair(this.tertiaryContainer(), this.tertiary(), 5, "relative_lighter", true, "farther") : void 0
    });
    return extendSpecVersion(super.tertiary(), "2025", color2025);
  }
  tertiaryDim() {
    return DynamicColor.fromPalette({
      name: "tertiary_dim",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => {
        if (s.variant === Variant.TONAL_SPOT) {
          return tMaxC(s.tertiaryPalette, 0, 90);
        } else {
          return tMaxC(s.tertiaryPalette);
        }
      },
      isBackground: true,
      background: (s) => this.surfaceContainerHigh(),
      contrastCurve: (s) => getCurve(4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.tertiaryDim(), this.tertiary(), 5, "darker", true, "farther")
    });
  }
  onTertiary() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_tertiary",
      palette: (s) => s.tertiaryPalette,
      background: (s) => s.platform === "phone" ? this.tertiary() : this.tertiaryDim(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(6) : getCurve(7)
    });
    return extendSpecVersion(super.onTertiary(), "2025", color2025);
  }
  tertiaryContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "tertiary_container",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => {
        if (s.platform === "watch") {
          return s.variant === Variant.TONAL_SPOT ? tMaxC(s.tertiaryPalette, 0, 90) : tMaxC(s.tertiaryPalette);
        } else {
          if (s.variant === Variant.NEUTRAL) {
            return s.isDark ? tMaxC(s.tertiaryPalette, 0, 93) : tMaxC(s.tertiaryPalette, 0, 96);
          } else if (s.variant === Variant.TONAL_SPOT) {
            return tMaxC(s.tertiaryPalette, 0, s.isDark ? 93 : 100);
          } else if (s.variant === Variant.EXPRESSIVE) {
            return tMaxC(s.tertiaryPalette, 75, Hct.isCyan(s.tertiaryPalette.hue) ? 88 : s.isDark ? 93 : 100);
          } else {
            return s.isDark ? tMaxC(s.tertiaryPalette, 0, 93) : tMaxC(s.tertiaryPalette, 72, 100);
          }
        }
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : void 0,
      toneDeltaPair: (s) => s.platform === "watch" ? new ToneDeltaPair(this.tertiaryContainer(), this.tertiaryDim(), 10, "darker", true, "farther") : void 0,
      contrastCurve: (s) => s.platform === "phone" && s.contrastLevel > 0 ? getCurve(1.5) : void 0
    });
    return extendSpecVersion(super.tertiaryContainer(), "2025", color2025);
  }
  onTertiaryContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_tertiary_container",
      palette: (s) => s.tertiaryPalette,
      background: (s) => this.tertiaryContainer(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(6) : getCurve(7)
    });
    return extendSpecVersion(super.onTertiaryContainer(), "2025", color2025);
  }
  tertiaryFixed() {
    const color2025 = DynamicColor.fromPalette({
      name: "tertiary_fixed",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => {
        let tempS = Object.assign({}, s, { isDark: false, contrastLevel: 0 });
        return this.tertiaryContainer().getTone(tempS);
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : void 0,
      contrastCurve: (s) => s.platform === "phone" && s.contrastLevel > 0 ? getCurve(1.5) : void 0
    });
    return extendSpecVersion(super.tertiaryFixed(), "2025", color2025);
  }
  tertiaryFixedDim() {
    const color2025 = DynamicColor.fromPalette({
      name: "tertiary_fixed_dim",
      palette: (s) => s.tertiaryPalette,
      tone: (s) => this.tertiaryFixed().getTone(s),
      isBackground: true,
      toneDeltaPair: (s) => new ToneDeltaPair(this.tertiaryFixedDim(), this.tertiaryFixed(), 5, "darker", true, "exact")
    });
    return extendSpecVersion(super.tertiaryFixedDim(), "2025", color2025);
  }
  onTertiaryFixed() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_tertiary_fixed",
      palette: (s) => s.tertiaryPalette,
      background: (s) => this.tertiaryFixedDim(),
      contrastCurve: (s) => getCurve(7)
    });
    return extendSpecVersion(super.onTertiaryFixed(), "2025", color2025);
  }
  onTertiaryFixedVariant() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_tertiary_fixed_variant",
      palette: (s) => s.tertiaryPalette,
      background: (s) => this.tertiaryFixedDim(),
      contrastCurve: (s) => getCurve(4.5)
    });
    return extendSpecVersion(super.onTertiaryFixedVariant(), "2025", color2025);
  }
  ////////////////////////////////////////////////////////////////
  // Errors [E]                                                 //
  ////////////////////////////////////////////////////////////////
  error() {
    const color2025 = DynamicColor.fromPalette({
      name: "error",
      palette: (s) => s.errorPalette,
      tone: (s) => {
        if (s.platform === "phone") {
          return s.isDark ? tMinC(s.errorPalette, 0, 98) : tMaxC(s.errorPalette);
        } else {
          return tMinC(s.errorPalette);
        }
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : this.surfaceContainerHigh(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(4.5) : getCurve(7),
      toneDeltaPair: (s) => s.platform === "phone" ? new ToneDeltaPair(this.errorContainer(), this.error(), 5, "relative_lighter", true, "farther") : void 0
    });
    return extendSpecVersion(super.error(), "2025", color2025);
  }
  errorDim() {
    return DynamicColor.fromPalette({
      name: "error_dim",
      palette: (s) => s.errorPalette,
      tone: (s) => tMinC(s.errorPalette),
      isBackground: true,
      background: (s) => this.surfaceContainerHigh(),
      contrastCurve: (s) => getCurve(4.5),
      toneDeltaPair: (s) => new ToneDeltaPair(this.errorDim(), this.error(), 5, "darker", true, "farther")
    });
  }
  onError() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_error",
      palette: (s) => s.errorPalette,
      background: (s) => s.platform === "phone" ? this.error() : this.errorDim(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(6) : getCurve(7)
    });
    return extendSpecVersion(super.onError(), "2025", color2025);
  }
  errorContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "error_container",
      palette: (s) => s.errorPalette,
      tone: (s) => {
        if (s.platform === "watch") {
          return 30;
        } else {
          return s.isDark ? tMinC(s.errorPalette, 30, 93) : tMaxC(s.errorPalette, 0, 90);
        }
      },
      isBackground: true,
      background: (s) => s.platform === "phone" ? this.highestSurface(s) : void 0,
      toneDeltaPair: (s) => s.platform === "watch" ? new ToneDeltaPair(this.errorContainer(), this.errorDim(), 10, "darker", true, "farther") : void 0,
      contrastCurve: (s) => s.platform === "phone" && s.contrastLevel > 0 ? getCurve(1.5) : void 0
    });
    return extendSpecVersion(super.errorContainer(), "2025", color2025);
  }
  onErrorContainer() {
    const color2025 = DynamicColor.fromPalette({
      name: "on_error_container",
      palette: (s) => s.errorPalette,
      background: (s) => this.errorContainer(),
      contrastCurve: (s) => s.platform === "phone" ? getCurve(4.5) : getCurve(7)
    });
    return extendSpecVersion(super.onErrorContainer(), "2025", color2025);
  }
  /////////////////////////////////////////////////////////////////
  // Remapped Colors                                             //
  /////////////////////////////////////////////////////////////////
  surfaceVariant() {
    const color2025 = Object.assign(this.surfaceContainerHighest().clone(), { name: "surface_variant" });
    return extendSpecVersion(super.surfaceVariant(), "2025", color2025);
  }
  surfaceTint() {
    const color2025 = Object.assign(this.primary().clone(), { name: "surface_tint" });
    return extendSpecVersion(super.surfaceTint(), "2025", color2025);
  }
  background() {
    const color2025 = Object.assign(this.surface().clone(), { name: "background" });
    return extendSpecVersion(super.background(), "2025", color2025);
  }
  onBackground() {
    const color2025 = Object.assign(this.onSurface().clone(), {
      name: "on_background",
      tone: (s) => {
        return s.platform === "watch" ? 100 : this.onSurface().getTone(s);
      }
    });
    return extendSpecVersion(super.onBackground(), "2025", color2025);
  }
};

// node_modules/@material/material-color-utilities/dynamiccolor/material_dynamic_colors.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var MaterialDynamicColors = class _MaterialDynamicColors {
  constructor() {
    this.allColors = [
      this.background(),
      this.onBackground(),
      this.surface(),
      this.surfaceDim(),
      this.surfaceBright(),
      this.surfaceContainerLowest(),
      this.surfaceContainerLow(),
      this.surfaceContainer(),
      this.surfaceContainerHigh(),
      this.surfaceContainerHighest(),
      this.onSurface(),
      this.onSurfaceVariant(),
      this.outline(),
      this.outlineVariant(),
      this.inverseSurface(),
      this.inverseOnSurface(),
      this.primary(),
      this.primaryDim(),
      this.onPrimary(),
      this.primaryContainer(),
      this.onPrimaryContainer(),
      this.primaryFixed(),
      this.primaryFixedDim(),
      this.onPrimaryFixed(),
      this.onPrimaryFixedVariant(),
      this.inversePrimary(),
      this.secondary(),
      this.secondaryDim(),
      this.onSecondary(),
      this.secondaryContainer(),
      this.onSecondaryContainer(),
      this.secondaryFixed(),
      this.secondaryFixedDim(),
      this.onSecondaryFixed(),
      this.onSecondaryFixedVariant(),
      this.tertiary(),
      this.tertiaryDim(),
      this.onTertiary(),
      this.tertiaryContainer(),
      this.onTertiaryContainer(),
      this.tertiaryFixed(),
      this.tertiaryFixedDim(),
      this.onTertiaryFixed(),
      this.onTertiaryFixedVariant(),
      this.error(),
      this.errorDim(),
      this.onError(),
      this.errorContainer(),
      this.onErrorContainer()
    ].filter((c2) => c2 !== void 0);
  }
  highestSurface(s) {
    return _MaterialDynamicColors.colorSpec.highestSurface(s);
  }
  ////////////////////////////////////////////////////////////////
  // Main Palettes                                              //
  ////////////////////////////////////////////////////////////////
  primaryPaletteKeyColor() {
    return _MaterialDynamicColors.colorSpec.primaryPaletteKeyColor();
  }
  secondaryPaletteKeyColor() {
    return _MaterialDynamicColors.colorSpec.secondaryPaletteKeyColor();
  }
  tertiaryPaletteKeyColor() {
    return _MaterialDynamicColors.colorSpec.tertiaryPaletteKeyColor();
  }
  neutralPaletteKeyColor() {
    return _MaterialDynamicColors.colorSpec.neutralPaletteKeyColor();
  }
  neutralVariantPaletteKeyColor() {
    return _MaterialDynamicColors.colorSpec.neutralVariantPaletteKeyColor();
  }
  errorPaletteKeyColor() {
    return _MaterialDynamicColors.colorSpec.errorPaletteKeyColor();
  }
  ////////////////////////////////////////////////////////////////
  // Surfaces [S]                                               //
  ////////////////////////////////////////////////////////////////
  background() {
    return _MaterialDynamicColors.colorSpec.background();
  }
  onBackground() {
    return _MaterialDynamicColors.colorSpec.onBackground();
  }
  surface() {
    return _MaterialDynamicColors.colorSpec.surface();
  }
  surfaceDim() {
    return _MaterialDynamicColors.colorSpec.surfaceDim();
  }
  surfaceBright() {
    return _MaterialDynamicColors.colorSpec.surfaceBright();
  }
  surfaceContainerLowest() {
    return _MaterialDynamicColors.colorSpec.surfaceContainerLowest();
  }
  surfaceContainerLow() {
    return _MaterialDynamicColors.colorSpec.surfaceContainerLow();
  }
  surfaceContainer() {
    return _MaterialDynamicColors.colorSpec.surfaceContainer();
  }
  surfaceContainerHigh() {
    return _MaterialDynamicColors.colorSpec.surfaceContainerHigh();
  }
  surfaceContainerHighest() {
    return _MaterialDynamicColors.colorSpec.surfaceContainerHighest();
  }
  onSurface() {
    return _MaterialDynamicColors.colorSpec.onSurface();
  }
  surfaceVariant() {
    return _MaterialDynamicColors.colorSpec.surfaceVariant();
  }
  onSurfaceVariant() {
    return _MaterialDynamicColors.colorSpec.onSurfaceVariant();
  }
  outline() {
    return _MaterialDynamicColors.colorSpec.outline();
  }
  outlineVariant() {
    return _MaterialDynamicColors.colorSpec.outlineVariant();
  }
  inverseSurface() {
    return _MaterialDynamicColors.colorSpec.inverseSurface();
  }
  inverseOnSurface() {
    return _MaterialDynamicColors.colorSpec.inverseOnSurface();
  }
  shadow() {
    return _MaterialDynamicColors.colorSpec.shadow();
  }
  scrim() {
    return _MaterialDynamicColors.colorSpec.scrim();
  }
  surfaceTint() {
    return _MaterialDynamicColors.colorSpec.surfaceTint();
  }
  ////////////////////////////////////////////////////////////////
  // Primaries [P]                                              //
  ////////////////////////////////////////////////////////////////
  primary() {
    return _MaterialDynamicColors.colorSpec.primary();
  }
  primaryDim() {
    return _MaterialDynamicColors.colorSpec.primaryDim();
  }
  onPrimary() {
    return _MaterialDynamicColors.colorSpec.onPrimary();
  }
  primaryContainer() {
    return _MaterialDynamicColors.colorSpec.primaryContainer();
  }
  onPrimaryContainer() {
    return _MaterialDynamicColors.colorSpec.onPrimaryContainer();
  }
  inversePrimary() {
    return _MaterialDynamicColors.colorSpec.inversePrimary();
  }
  /////////////////////////////////////////////////////////////////
  // Primary Fixed [PF]                                          //
  /////////////////////////////////////////////////////////////////
  primaryFixed() {
    return _MaterialDynamicColors.colorSpec.primaryFixed();
  }
  primaryFixedDim() {
    return _MaterialDynamicColors.colorSpec.primaryFixedDim();
  }
  onPrimaryFixed() {
    return _MaterialDynamicColors.colorSpec.onPrimaryFixed();
  }
  onPrimaryFixedVariant() {
    return _MaterialDynamicColors.colorSpec.onPrimaryFixedVariant();
  }
  ////////////////////////////////////////////////////////////////
  // Secondaries [Q]                                            //
  ////////////////////////////////////////////////////////////////
  secondary() {
    return _MaterialDynamicColors.colorSpec.secondary();
  }
  secondaryDim() {
    return _MaterialDynamicColors.colorSpec.secondaryDim();
  }
  onSecondary() {
    return _MaterialDynamicColors.colorSpec.onSecondary();
  }
  secondaryContainer() {
    return _MaterialDynamicColors.colorSpec.secondaryContainer();
  }
  onSecondaryContainer() {
    return _MaterialDynamicColors.colorSpec.onSecondaryContainer();
  }
  /////////////////////////////////////////////////////////////////
  // Secondary Fixed [QF]                                        //
  /////////////////////////////////////////////////////////////////
  secondaryFixed() {
    return _MaterialDynamicColors.colorSpec.secondaryFixed();
  }
  secondaryFixedDim() {
    return _MaterialDynamicColors.colorSpec.secondaryFixedDim();
  }
  onSecondaryFixed() {
    return _MaterialDynamicColors.colorSpec.onSecondaryFixed();
  }
  onSecondaryFixedVariant() {
    return _MaterialDynamicColors.colorSpec.onSecondaryFixedVariant();
  }
  ////////////////////////////////////////////////////////////////
  // Tertiaries [T]                                             //
  ////////////////////////////////////////////////////////////////
  tertiary() {
    return _MaterialDynamicColors.colorSpec.tertiary();
  }
  tertiaryDim() {
    return _MaterialDynamicColors.colorSpec.tertiaryDim();
  }
  onTertiary() {
    return _MaterialDynamicColors.colorSpec.onTertiary();
  }
  tertiaryContainer() {
    return _MaterialDynamicColors.colorSpec.tertiaryContainer();
  }
  onTertiaryContainer() {
    return _MaterialDynamicColors.colorSpec.onTertiaryContainer();
  }
  /////////////////////////////////////////////////////////////////
  // Tertiary Fixed [TF]                                         //
  /////////////////////////////////////////////////////////////////
  tertiaryFixed() {
    return _MaterialDynamicColors.colorSpec.tertiaryFixed();
  }
  tertiaryFixedDim() {
    return _MaterialDynamicColors.colorSpec.tertiaryFixedDim();
  }
  onTertiaryFixed() {
    return _MaterialDynamicColors.colorSpec.onTertiaryFixed();
  }
  onTertiaryFixedVariant() {
    return _MaterialDynamicColors.colorSpec.onTertiaryFixedVariant();
  }
  ////////////////////////////////////////////////////////////////
  // Errors [E]                                                 //
  ////////////////////////////////////////////////////////////////
  error() {
    return _MaterialDynamicColors.colorSpec.error();
  }
  errorDim() {
    return _MaterialDynamicColors.colorSpec.errorDim();
  }
  onError() {
    return _MaterialDynamicColors.colorSpec.onError();
  }
  errorContainer() {
    return _MaterialDynamicColors.colorSpec.errorContainer();
  }
  onErrorContainer() {
    return _MaterialDynamicColors.colorSpec.onErrorContainer();
  }
  // Static variables are deprecated. Use the instance methods to get correct
  // specs based on request.
  /** @deprecated Use highestSurface() instead. */
  static highestSurface(s) {
    return _MaterialDynamicColors.colorSpec.highestSurface(s);
  }
};
MaterialDynamicColors.contentAccentToneDelta = 15;
MaterialDynamicColors.colorSpec = new ColorSpecDelegateImpl2025();
MaterialDynamicColors.primaryPaletteKeyColor = MaterialDynamicColors.colorSpec.primaryPaletteKeyColor();
MaterialDynamicColors.secondaryPaletteKeyColor = MaterialDynamicColors.colorSpec.secondaryPaletteKeyColor();
MaterialDynamicColors.tertiaryPaletteKeyColor = MaterialDynamicColors.colorSpec.tertiaryPaletteKeyColor();
MaterialDynamicColors.neutralPaletteKeyColor = MaterialDynamicColors.colorSpec.neutralPaletteKeyColor();
MaterialDynamicColors.neutralVariantPaletteKeyColor = MaterialDynamicColors.colorSpec.neutralVariantPaletteKeyColor();
MaterialDynamicColors.background = MaterialDynamicColors.colorSpec.background();
MaterialDynamicColors.onBackground = MaterialDynamicColors.colorSpec.onBackground();
MaterialDynamicColors.surface = MaterialDynamicColors.colorSpec.surface();
MaterialDynamicColors.surfaceDim = MaterialDynamicColors.colorSpec.surfaceDim();
MaterialDynamicColors.surfaceBright = MaterialDynamicColors.colorSpec.surfaceBright();
MaterialDynamicColors.surfaceContainerLowest = MaterialDynamicColors.colorSpec.surfaceContainerLowest();
MaterialDynamicColors.surfaceContainerLow = MaterialDynamicColors.colorSpec.surfaceContainerLow();
MaterialDynamicColors.surfaceContainer = MaterialDynamicColors.colorSpec.surfaceContainer();
MaterialDynamicColors.surfaceContainerHigh = MaterialDynamicColors.colorSpec.surfaceContainerHigh();
MaterialDynamicColors.surfaceContainerHighest = MaterialDynamicColors.colorSpec.surfaceContainerHighest();
MaterialDynamicColors.onSurface = MaterialDynamicColors.colorSpec.onSurface();
MaterialDynamicColors.surfaceVariant = MaterialDynamicColors.colorSpec.surfaceVariant();
MaterialDynamicColors.onSurfaceVariant = MaterialDynamicColors.colorSpec.onSurfaceVariant();
MaterialDynamicColors.inverseSurface = MaterialDynamicColors.colorSpec.inverseSurface();
MaterialDynamicColors.inverseOnSurface = MaterialDynamicColors.colorSpec.inverseOnSurface();
MaterialDynamicColors.outline = MaterialDynamicColors.colorSpec.outline();
MaterialDynamicColors.outlineVariant = MaterialDynamicColors.colorSpec.outlineVariant();
MaterialDynamicColors.shadow = MaterialDynamicColors.colorSpec.shadow();
MaterialDynamicColors.scrim = MaterialDynamicColors.colorSpec.scrim();
MaterialDynamicColors.surfaceTint = MaterialDynamicColors.colorSpec.surfaceTint();
MaterialDynamicColors.primary = MaterialDynamicColors.colorSpec.primary();
MaterialDynamicColors.onPrimary = MaterialDynamicColors.colorSpec.onPrimary();
MaterialDynamicColors.primaryContainer = MaterialDynamicColors.colorSpec.primaryContainer();
MaterialDynamicColors.onPrimaryContainer = MaterialDynamicColors.colorSpec.onPrimaryContainer();
MaterialDynamicColors.inversePrimary = MaterialDynamicColors.colorSpec.inversePrimary();
MaterialDynamicColors.secondary = MaterialDynamicColors.colorSpec.secondary();
MaterialDynamicColors.onSecondary = MaterialDynamicColors.colorSpec.onSecondary();
MaterialDynamicColors.secondaryContainer = MaterialDynamicColors.colorSpec.secondaryContainer();
MaterialDynamicColors.onSecondaryContainer = MaterialDynamicColors.colorSpec.onSecondaryContainer();
MaterialDynamicColors.tertiary = MaterialDynamicColors.colorSpec.tertiary();
MaterialDynamicColors.onTertiary = MaterialDynamicColors.colorSpec.onTertiary();
MaterialDynamicColors.tertiaryContainer = MaterialDynamicColors.colorSpec.tertiaryContainer();
MaterialDynamicColors.onTertiaryContainer = MaterialDynamicColors.colorSpec.onTertiaryContainer();
MaterialDynamicColors.error = MaterialDynamicColors.colorSpec.error();
MaterialDynamicColors.onError = MaterialDynamicColors.colorSpec.onError();
MaterialDynamicColors.errorContainer = MaterialDynamicColors.colorSpec.errorContainer();
MaterialDynamicColors.onErrorContainer = MaterialDynamicColors.colorSpec.onErrorContainer();
MaterialDynamicColors.primaryFixed = MaterialDynamicColors.colorSpec.primaryFixed();
MaterialDynamicColors.primaryFixedDim = MaterialDynamicColors.colorSpec.primaryFixedDim();
MaterialDynamicColors.onPrimaryFixed = MaterialDynamicColors.colorSpec.onPrimaryFixed();
MaterialDynamicColors.onPrimaryFixedVariant = MaterialDynamicColors.colorSpec.onPrimaryFixedVariant();
MaterialDynamicColors.secondaryFixed = MaterialDynamicColors.colorSpec.secondaryFixed();
MaterialDynamicColors.secondaryFixedDim = MaterialDynamicColors.colorSpec.secondaryFixedDim();
MaterialDynamicColors.onSecondaryFixed = MaterialDynamicColors.colorSpec.onSecondaryFixed();
MaterialDynamicColors.onSecondaryFixedVariant = MaterialDynamicColors.colorSpec.onSecondaryFixedVariant();
MaterialDynamicColors.tertiaryFixed = MaterialDynamicColors.colorSpec.tertiaryFixed();
MaterialDynamicColors.tertiaryFixedDim = MaterialDynamicColors.colorSpec.tertiaryFixedDim();
MaterialDynamicColors.onTertiaryFixed = MaterialDynamicColors.colorSpec.onTertiaryFixed();
MaterialDynamicColors.onTertiaryFixedVariant = MaterialDynamicColors.colorSpec.onTertiaryFixedVariant();

// node_modules/@material/material-color-utilities/dynamiccolor/dynamic_scheme.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var DynamicScheme = class _DynamicScheme {
  static maybeFallbackSpecVersion(specVersion, variant) {
    switch (variant) {
      case Variant.EXPRESSIVE:
      case Variant.VIBRANT:
      case Variant.TONAL_SPOT:
      case Variant.NEUTRAL:
        return specVersion;
      default:
        return "2021";
    }
  }
  constructor(args) {
    this.sourceColorArgb = args.sourceColorHct.toInt();
    this.variant = args.variant;
    this.contrastLevel = args.contrastLevel;
    this.isDark = args.isDark;
    this.platform = args.platform ?? "phone";
    this.specVersion = _DynamicScheme.maybeFallbackSpecVersion(args.specVersion ?? "2021", this.variant);
    this.sourceColorHct = args.sourceColorHct;
    this.primaryPalette = args.primaryPalette ?? getSpec2(this.specVersion).getPrimaryPalette(this.variant, args.sourceColorHct, this.isDark, this.platform, this.contrastLevel);
    this.secondaryPalette = args.secondaryPalette ?? getSpec2(this.specVersion).getSecondaryPalette(this.variant, args.sourceColorHct, this.isDark, this.platform, this.contrastLevel);
    this.tertiaryPalette = args.tertiaryPalette ?? getSpec2(this.specVersion).getTertiaryPalette(this.variant, args.sourceColorHct, this.isDark, this.platform, this.contrastLevel);
    this.neutralPalette = args.neutralPalette ?? getSpec2(this.specVersion).getNeutralPalette(this.variant, args.sourceColorHct, this.isDark, this.platform, this.contrastLevel);
    this.neutralVariantPalette = args.neutralVariantPalette ?? getSpec2(this.specVersion).getNeutralVariantPalette(this.variant, args.sourceColorHct, this.isDark, this.platform, this.contrastLevel);
    this.errorPalette = args.errorPalette ?? getSpec2(this.specVersion).getErrorPalette(this.variant, args.sourceColorHct, this.isDark, this.platform, this.contrastLevel) ?? TonalPalette.fromHueAndChroma(25, 84);
    this.colors = new MaterialDynamicColors();
  }
  toString() {
    return `Scheme: variant=${Variant[this.variant]}, mode=${this.isDark ? "dark" : "light"}, platform=${this.platform}, contrastLevel=${this.contrastLevel.toFixed(1)}, seed=${this.sourceColorHct.toString()}, specVersion=${this.specVersion}`;
  }
  /**
   * Returns a new hue based on a piecewise function and input color hue.
   *
   * For example, for the following function:
   * result = 26 if 0 <= hue < 101
   * result = 39 if 101 <= hue < 210
   * result = 28 if 210 <= hue < 360
   *
   * call the function as:
   *
   * const hueBreakpoints = [0, 101, 210, 360];
   * const hues = [26, 39, 28];
   * const result = scheme.piecewise(hue, hueBreakpoints, hues);
   *
   * @param sourceColorHct The input value.
   * @param hueBreakpoints The breakpoints, in sorted order. No default lower or
   *     upper bounds are assumed.
   * @param hues The hues that should be applied when source color's hue is >=
   *     the same index in hueBrakpoints array, and < the hue at the next index
   *     in hueBrakpoints array. Otherwise, the source color's hue is returned.
   */
  static getPiecewiseHue(sourceColorHct, hueBreakpoints, hues) {
    const size = Math.min(hueBreakpoints.length - 1, hues.length);
    const sourceHue = sourceColorHct.hue;
    for (let i = 0; i < size; i++) {
      if (sourceHue >= hueBreakpoints[i] && sourceHue < hueBreakpoints[i + 1]) {
        return sanitizeDegreesDouble(hues[i]);
      }
    }
    return sourceHue;
  }
  /**
   * Returns a shifted hue based on a piecewise function and input color hue.
   *
   * For example, for the following function:
   * result = hue + 26 if 0 <= hue < 101
   * result = hue - 39 if 101 <= hue < 210
   * result = hue + 28 if 210 <= hue < 360
   *
   * call the function as:
   *
   * const hueBreakpoints = [0, 101, 210, 360];
   * const hues = [26, -39, 28];
   * const result = scheme.getRotatedHue(hue, hueBreakpoints, hues);
   *
   * @param sourceColorHct the source color of the theme, in HCT.
   * @param hueBreakpoints The "breakpoints", i.e. the hues at which a rotation
   *     should be apply. No default lower or upper bounds are assumed.
   * @param rotations The rotation that should be applied when source color's
   *     hue is >= the same index in hues array, and < the hue at the next
   *     index in hues array. Otherwise, the source color's hue is returned.
   */
  static getRotatedHue(sourceColorHct, hueBreakpoints, rotations) {
    let rotation = _DynamicScheme.getPiecewiseHue(sourceColorHct, hueBreakpoints, rotations);
    if (Math.min(hueBreakpoints.length - 1, rotations.length) <= 0) {
      rotation = 0;
    }
    return sanitizeDegreesDouble(sourceColorHct.hue + rotation);
  }
  getArgb(dynamicColor) {
    return dynamicColor.getArgb(this);
  }
  getHct(dynamicColor) {
    return dynamicColor.getHct(this);
  }
  // Palette key colors
  get primaryPaletteKeyColor() {
    return this.getArgb(this.colors.primaryPaletteKeyColor());
  }
  get secondaryPaletteKeyColor() {
    return this.getArgb(this.colors.secondaryPaletteKeyColor());
  }
  get tertiaryPaletteKeyColor() {
    return this.getArgb(this.colors.tertiaryPaletteKeyColor());
  }
  get neutralPaletteKeyColor() {
    return this.getArgb(this.colors.neutralPaletteKeyColor());
  }
  get neutralVariantPaletteKeyColor() {
    return this.getArgb(this.colors.neutralVariantPaletteKeyColor());
  }
  get errorPaletteKeyColor() {
    return this.getArgb(this.colors.errorPaletteKeyColor());
  }
  // Surface colors
  get background() {
    return this.getArgb(this.colors.background());
  }
  get onBackground() {
    return this.getArgb(this.colors.onBackground());
  }
  get surface() {
    return this.getArgb(this.colors.surface());
  }
  get surfaceDim() {
    return this.getArgb(this.colors.surfaceDim());
  }
  get surfaceBright() {
    return this.getArgb(this.colors.surfaceBright());
  }
  get surfaceContainerLowest() {
    return this.getArgb(this.colors.surfaceContainerLowest());
  }
  get surfaceContainerLow() {
    return this.getArgb(this.colors.surfaceContainerLow());
  }
  get surfaceContainer() {
    return this.getArgb(this.colors.surfaceContainer());
  }
  get surfaceContainerHigh() {
    return this.getArgb(this.colors.surfaceContainerHigh());
  }
  get surfaceContainerHighest() {
    return this.getArgb(this.colors.surfaceContainerHighest());
  }
  get onSurface() {
    return this.getArgb(this.colors.onSurface());
  }
  get surfaceVariant() {
    return this.getArgb(this.colors.surfaceVariant());
  }
  get onSurfaceVariant() {
    return this.getArgb(this.colors.onSurfaceVariant());
  }
  get inverseSurface() {
    return this.getArgb(this.colors.inverseSurface());
  }
  get inverseOnSurface() {
    return this.getArgb(this.colors.inverseOnSurface());
  }
  get outline() {
    return this.getArgb(this.colors.outline());
  }
  get outlineVariant() {
    return this.getArgb(this.colors.outlineVariant());
  }
  get shadow() {
    return this.getArgb(this.colors.shadow());
  }
  get scrim() {
    return this.getArgb(this.colors.scrim());
  }
  get surfaceTint() {
    return this.getArgb(this.colors.surfaceTint());
  }
  // Primary colors
  get primary() {
    return this.getArgb(this.colors.primary());
  }
  get primaryDim() {
    const primaryDim = this.colors.primaryDim();
    if (primaryDim === void 0) {
      throw new Error("`primaryDim` color is undefined prior to 2025 spec.");
    }
    return this.getArgb(primaryDim);
  }
  get onPrimary() {
    return this.getArgb(this.colors.onPrimary());
  }
  get primaryContainer() {
    return this.getArgb(this.colors.primaryContainer());
  }
  get onPrimaryContainer() {
    return this.getArgb(this.colors.onPrimaryContainer());
  }
  get primaryFixed() {
    return this.getArgb(this.colors.primaryFixed());
  }
  get primaryFixedDim() {
    return this.getArgb(this.colors.primaryFixedDim());
  }
  get onPrimaryFixed() {
    return this.getArgb(this.colors.onPrimaryFixed());
  }
  get onPrimaryFixedVariant() {
    return this.getArgb(this.colors.onPrimaryFixedVariant());
  }
  get inversePrimary() {
    return this.getArgb(this.colors.inversePrimary());
  }
  // Secondary colors
  get secondary() {
    return this.getArgb(this.colors.secondary());
  }
  get secondaryDim() {
    const secondaryDim = this.colors.secondaryDim();
    if (secondaryDim === void 0) {
      throw new Error("`secondaryDim` color is undefined prior to 2025 spec.");
    }
    return this.getArgb(secondaryDim);
  }
  get onSecondary() {
    return this.getArgb(this.colors.onSecondary());
  }
  get secondaryContainer() {
    return this.getArgb(this.colors.secondaryContainer());
  }
  get onSecondaryContainer() {
    return this.getArgb(this.colors.onSecondaryContainer());
  }
  get secondaryFixed() {
    return this.getArgb(this.colors.secondaryFixed());
  }
  get secondaryFixedDim() {
    return this.getArgb(this.colors.secondaryFixedDim());
  }
  get onSecondaryFixed() {
    return this.getArgb(this.colors.onSecondaryFixed());
  }
  get onSecondaryFixedVariant() {
    return this.getArgb(this.colors.onSecondaryFixedVariant());
  }
  // Tertiary colors
  get tertiary() {
    return this.getArgb(this.colors.tertiary());
  }
  get tertiaryDim() {
    const tertiaryDim = this.colors.tertiaryDim();
    if (tertiaryDim === void 0) {
      throw new Error("`tertiaryDim` color is undefined prior to 2025 spec.");
    }
    return this.getArgb(tertiaryDim);
  }
  get onTertiary() {
    return this.getArgb(this.colors.onTertiary());
  }
  get tertiaryContainer() {
    return this.getArgb(this.colors.tertiaryContainer());
  }
  get onTertiaryContainer() {
    return this.getArgb(this.colors.onTertiaryContainer());
  }
  get tertiaryFixed() {
    return this.getArgb(this.colors.tertiaryFixed());
  }
  get tertiaryFixedDim() {
    return this.getArgb(this.colors.tertiaryFixedDim());
  }
  get onTertiaryFixed() {
    return this.getArgb(this.colors.onTertiaryFixed());
  }
  get onTertiaryFixedVariant() {
    return this.getArgb(this.colors.onTertiaryFixedVariant());
  }
  // Error colors
  get error() {
    return this.getArgb(this.colors.error());
  }
  get errorDim() {
    const errorDim = this.colors.errorDim();
    if (errorDim === void 0) {
      throw new Error("`errorDim` color is undefined prior to 2025 spec.");
    }
    return this.getArgb(errorDim);
  }
  get onError() {
    return this.getArgb(this.colors.onError());
  }
  get errorContainer() {
    return this.getArgb(this.colors.errorContainer());
  }
  get onErrorContainer() {
    return this.getArgb(this.colors.onErrorContainer());
  }
};
DynamicScheme.DEFAULT_SPEC_VERSION = "2021";
DynamicScheme.DEFAULT_PLATFORM = "phone";
var DynamicSchemePalettesDelegateImpl2021 = class {
  //////////////////////////////////////////////////////////////////
  // Scheme Palettes                                              //
  //////////////////////////////////////////////////////////////////
  getPrimaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.CONTENT:
      case Variant.FIDELITY:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, sourceColorHct.chroma);
      case Variant.FRUIT_SALAD:
        return TonalPalette.fromHueAndChroma(sanitizeDegreesDouble(sourceColorHct.hue - 50), 48);
      case Variant.MONOCHROME:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 0);
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 12);
      case Variant.RAINBOW:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 48);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 36);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(sanitizeDegreesDouble(sourceColorHct.hue + 240), 40);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 200);
      default:
        throw new Error(`Unsupported variant: ${variant}`);
    }
  }
  getSecondaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.CONTENT:
      case Variant.FIDELITY:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, Math.max(sourceColorHct.chroma - 32, sourceColorHct.chroma * 0.5));
      case Variant.FRUIT_SALAD:
        return TonalPalette.fromHueAndChroma(sanitizeDegreesDouble(sourceColorHct.hue - 50), 36);
      case Variant.MONOCHROME:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 0);
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 8);
      case Variant.RAINBOW:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 16);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 16);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 21, 51, 121, 151, 191, 271, 321, 360], [45, 95, 45, 20, 45, 90, 45, 45, 45]), 24);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 41, 61, 101, 131, 181, 251, 301, 360], [18, 15, 10, 12, 15, 18, 15, 12, 12]), 24);
      default:
        throw new Error(`Unsupported variant: ${variant}`);
    }
  }
  getTertiaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.CONTENT:
        return TonalPalette.fromHct(DislikeAnalyzer.fixIfDisliked(new TemperatureCache(sourceColorHct).analogous(
          /* count= */
          3,
          /* divisions= */
          6
        )[2]));
      case Variant.FIDELITY:
        return TonalPalette.fromHct(DislikeAnalyzer.fixIfDisliked(new TemperatureCache(sourceColorHct).complement));
      case Variant.FRUIT_SALAD:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 36);
      case Variant.MONOCHROME:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 0);
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 16);
      case Variant.RAINBOW:
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sanitizeDegreesDouble(sourceColorHct.hue + 60), 24);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 21, 51, 121, 151, 191, 271, 321, 360], [120, 120, 20, 45, 20, 15, 20, 120, 120]), 32);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 41, 61, 101, 131, 181, 251, 301, 360], [35, 30, 20, 25, 30, 35, 30, 25, 25]), 32);
      default:
        throw new Error(`Unsupported variant: ${variant}`);
    }
  }
  getNeutralPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.CONTENT:
      case Variant.FIDELITY:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, sourceColorHct.chroma / 8);
      case Variant.FRUIT_SALAD:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 10);
      case Variant.MONOCHROME:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 0);
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 2);
      case Variant.RAINBOW:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 0);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 6);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(sanitizeDegreesDouble(sourceColorHct.hue + 15), 8);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 10);
      default:
        throw new Error(`Unsupported variant: ${variant}`);
    }
  }
  getNeutralVariantPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.CONTENT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, sourceColorHct.chroma / 8 + 4);
      case Variant.FIDELITY:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, sourceColorHct.chroma / 8 + 4);
      case Variant.FRUIT_SALAD:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 16);
      case Variant.MONOCHROME:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 0);
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 2);
      case Variant.RAINBOW:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 0);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 8);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(sanitizeDegreesDouble(sourceColorHct.hue + 15), 12);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 12);
      default:
        throw new Error(`Unsupported variant: ${variant}`);
    }
  }
  getErrorPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    return void 0;
  }
};
var DynamicSchemePalettesDelegateImpl2025 = class _DynamicSchemePalettesDelegateImpl2025 extends DynamicSchemePalettesDelegateImpl2021 {
  //////////////////////////////////////////////////////////////////
  // Scheme Palettes                                              //
  //////////////////////////////////////////////////////////////////
  getPrimaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, platform === "phone" ? Hct.isBlue(sourceColorHct.hue) ? 12 : 8 : Hct.isBlue(sourceColorHct.hue) ? 16 : 12);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, platform === "phone" && isDark ? 26 : 32);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, platform === "phone" ? isDark ? 36 : 48 : 40);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, platform === "phone" ? 74 : 56);
      default:
        return super.getPrimaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel);
    }
  }
  getSecondaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, platform === "phone" ? Hct.isBlue(sourceColorHct.hue) ? 6 : 4 : Hct.isBlue(sourceColorHct.hue) ? 10 : 6);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, 16);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 105, 140, 204, 253, 278, 300, 333, 360], [-160, 155, -100, 96, -96, -156, -165, -160]), platform === "phone" ? isDark ? 16 : 24 : 24);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 38, 105, 140, 333, 360], [-14, 10, -14, 10, -14]), platform === "phone" ? 56 : 36);
      default:
        return super.getSecondaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel);
    }
  }
  getTertiaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 38, 105, 161, 204, 278, 333, 360], [-32, 26, 10, -39, 24, -15, -32]), platform === "phone" ? 20 : 36);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 20, 71, 161, 333, 360], [-40, 48, -32, 40, -32]), platform === "phone" ? 28 : 32);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 105, 140, 204, 253, 278, 300, 333, 360], [-165, 160, -105, 101, -101, -160, -170, -165]), 48);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(DynamicScheme.getRotatedHue(sourceColorHct, [0, 38, 71, 105, 140, 161, 253, 333, 360], [-72, 35, 24, -24, 62, 50, 62, -72]), 56);
      default:
        return super.getTertiaryPalette(variant, sourceColorHct, isDark, platform, contrastLevel);
    }
  }
  static getExpressiveNeutralHue(sourceColorHct) {
    const hue3 = DynamicScheme.getRotatedHue(sourceColorHct, [0, 71, 124, 253, 278, 300, 360], [10, 0, 10, 0, 10, 0]);
    return hue3;
  }
  static getExpressiveNeutralChroma(sourceColorHct, isDark, platform) {
    const neutralHue = _DynamicSchemePalettesDelegateImpl2025.getExpressiveNeutralHue(sourceColorHct);
    return platform === "phone" ? isDark ? Hct.isYellow(neutralHue) ? 6 : 14 : 18 : 12;
  }
  static getVibrantNeutralHue(sourceColorHct) {
    return DynamicScheme.getRotatedHue(sourceColorHct, [0, 38, 105, 140, 333, 360], [-14, 10, -14, 10, -14]);
  }
  static getVibrantNeutralChroma(sourceColorHct, platform) {
    const neutralHue = _DynamicSchemePalettesDelegateImpl2025.getVibrantNeutralHue(sourceColorHct);
    return platform === "phone" ? 28 : Hct.isBlue(neutralHue) ? 28 : 20;
  }
  getNeutralPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, platform === "phone" ? 1.4 : 6);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, platform === "phone" ? 5 : 10);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(_DynamicSchemePalettesDelegateImpl2025.getExpressiveNeutralHue(sourceColorHct), _DynamicSchemePalettesDelegateImpl2025.getExpressiveNeutralChroma(sourceColorHct, isDark, platform));
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(_DynamicSchemePalettesDelegateImpl2025.getVibrantNeutralHue(sourceColorHct), _DynamicSchemePalettesDelegateImpl2025.getVibrantNeutralChroma(sourceColorHct, platform));
      default:
        return super.getNeutralPalette(variant, sourceColorHct, isDark, platform, contrastLevel);
    }
  }
  getNeutralVariantPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    switch (variant) {
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, (platform === "phone" ? 1.4 : 6) * 2.2);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(sourceColorHct.hue, (platform === "phone" ? 5 : 10) * 1.7);
      case Variant.EXPRESSIVE:
        const expressiveNeutralHue = _DynamicSchemePalettesDelegateImpl2025.getExpressiveNeutralHue(sourceColorHct);
        const expressiveNeutralChroma = _DynamicSchemePalettesDelegateImpl2025.getExpressiveNeutralChroma(sourceColorHct, isDark, platform);
        return TonalPalette.fromHueAndChroma(expressiveNeutralHue, expressiveNeutralChroma * (expressiveNeutralHue >= 105 && expressiveNeutralHue < 125 ? 1.6 : 2.3));
      case Variant.VIBRANT:
        const vibrantNeutralHue = _DynamicSchemePalettesDelegateImpl2025.getVibrantNeutralHue(sourceColorHct);
        const vibrantNeutralChroma = _DynamicSchemePalettesDelegateImpl2025.getVibrantNeutralChroma(sourceColorHct, platform);
        return TonalPalette.fromHueAndChroma(vibrantNeutralHue, vibrantNeutralChroma * 1.29);
      default:
        return super.getNeutralVariantPalette(variant, sourceColorHct, isDark, platform, contrastLevel);
    }
  }
  getErrorPalette(variant, sourceColorHct, isDark, platform, contrastLevel) {
    const errorHue = DynamicScheme.getPiecewiseHue(sourceColorHct, [0, 3, 13, 23, 33, 43, 153, 273, 360], [12, 22, 32, 12, 22, 32, 22, 12]);
    switch (variant) {
      case Variant.NEUTRAL:
        return TonalPalette.fromHueAndChroma(errorHue, platform === "phone" ? 50 : 40);
      case Variant.TONAL_SPOT:
        return TonalPalette.fromHueAndChroma(errorHue, platform === "phone" ? 60 : 48);
      case Variant.EXPRESSIVE:
        return TonalPalette.fromHueAndChroma(errorHue, platform === "phone" ? 64 : 48);
      case Variant.VIBRANT:
        return TonalPalette.fromHueAndChroma(errorHue, platform === "phone" ? 80 : 60);
      default:
        return super.getErrorPalette(variant, sourceColorHct, isDark, platform, contrastLevel);
    }
  }
};
var spec20212 = new DynamicSchemePalettesDelegateImpl2021();
var spec20252 = new DynamicSchemePalettesDelegateImpl2025();
function getSpec2(specVersion) {
  return specVersion === "2025" ? spec20252 : spec20212;
}

// node_modules/@material/material-color-utilities/palettes/core_palette.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/quantize/lab_point_provider.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/quantize/quantizer_wsmeans.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/quantize/quantizer_map.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/quantize/quantizer_wu.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/quantize/quantizer_celebi.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/scheme/scheme.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/scheme/scheme_android.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/scheme/scheme_content.js
/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/scheme/scheme_expressive.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/scheme/scheme_fidelity.js
/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var SchemeFidelity = class extends DynamicScheme {
  constructor(sourceColorHct, isDark, contrastLevel, specVersion = DynamicScheme.DEFAULT_SPEC_VERSION, platform = DynamicScheme.DEFAULT_PLATFORM) {
    super({
      sourceColorHct,
      variant: Variant.FIDELITY,
      contrastLevel,
      isDark,
      platform,
      specVersion
    });
  }
};

// node_modules/@material/material-color-utilities/scheme/scheme_fruit_salad.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/scheme/scheme_monochrome.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var SchemeMonochrome = class extends DynamicScheme {
  constructor(sourceColorHct, isDark, contrastLevel, specVersion = DynamicScheme.DEFAULT_SPEC_VERSION, platform = DynamicScheme.DEFAULT_PLATFORM) {
    super({
      sourceColorHct,
      variant: Variant.MONOCHROME,
      contrastLevel,
      isDark,
      platform,
      specVersion
    });
  }
};

// node_modules/@material/material-color-utilities/scheme/scheme_neutral.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var SchemeNeutral = class extends DynamicScheme {
  constructor(sourceColorHct, isDark, contrastLevel, specVersion = DynamicScheme.DEFAULT_SPEC_VERSION, platform = DynamicScheme.DEFAULT_PLATFORM) {
    super({
      sourceColorHct,
      variant: Variant.NEUTRAL,
      contrastLevel,
      isDark,
      platform,
      specVersion
    });
  }
};

// node_modules/@material/material-color-utilities/scheme/scheme_rainbow.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/scheme/scheme_tonal_spot.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var SchemeTonalSpot = class extends DynamicScheme {
  constructor(sourceColorHct, isDark, contrastLevel, specVersion = DynamicScheme.DEFAULT_SPEC_VERSION, platform = DynamicScheme.DEFAULT_PLATFORM) {
    super({
      sourceColorHct,
      variant: Variant.TONAL_SPOT,
      contrastLevel,
      isDark,
      platform,
      specVersion
    });
  }
};

// node_modules/@material/material-color-utilities/scheme/scheme_vibrant.js
/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/score/score.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var SCORE_OPTION_DEFAULTS = {
  desired: 4,
  fallbackColorARGB: 4282549748,
  filter: true
  // Avoid unsuitable colors.
};
function compare(a, b) {
  if (a.score > b.score) {
    return -1;
  } else if (a.score < b.score) {
    return 1;
  }
  return 0;
}
var Score = class _Score {
  constructor() {
  }
  /**
   * Given a map with keys of colors and values of how often the color appears,
   * rank the colors based on suitability for being used for a UI theme.
   *
   * @param colorsToPopulation map with keys of colors and values of how often
   *     the color appears, usually from a source image.
   * @param {ScoreOptions} options optional parameters.
   * @return Colors sorted by suitability for a UI theme. The most suitable
   *     color is the first item, the least suitable is the last. There will
   *     always be at least one color returned. If all the input colors
   *     were not suitable for a theme, a default fallback color will be
   *     provided, Google Blue.
   */
  static score(colorsToPopulation, options) {
    const { desired, fallbackColorARGB, filter } = { ...SCORE_OPTION_DEFAULTS, ...options };
    const colorsHct = [];
    const huePopulation = new Array(360).fill(0);
    let populationSum = 0;
    for (const [argb, population] of colorsToPopulation.entries()) {
      const hct = Hct.fromInt(argb);
      colorsHct.push(hct);
      const hue3 = Math.floor(hct.hue);
      huePopulation[hue3] += population;
      populationSum += population;
    }
    const hueExcitedProportions = new Array(360).fill(0);
    for (let hue3 = 0; hue3 < 360; hue3++) {
      const proportion = huePopulation[hue3] / populationSum;
      for (let i = hue3 - 14; i < hue3 + 16; i++) {
        const neighborHue = sanitizeDegreesInt(i);
        hueExcitedProportions[neighborHue] += proportion;
      }
    }
    const scoredHct = new Array();
    for (const hct of colorsHct) {
      const hue3 = sanitizeDegreesInt(Math.round(hct.hue));
      const proportion = hueExcitedProportions[hue3];
      if (filter && (hct.chroma < _Score.CUTOFF_CHROMA || proportion <= _Score.CUTOFF_EXCITED_PROPORTION)) {
        continue;
      }
      const proportionScore = proportion * 100 * _Score.WEIGHT_PROPORTION;
      const chromaWeight = hct.chroma < _Score.TARGET_CHROMA ? _Score.WEIGHT_CHROMA_BELOW : _Score.WEIGHT_CHROMA_ABOVE;
      const chromaScore = (hct.chroma - _Score.TARGET_CHROMA) * chromaWeight;
      const score = proportionScore + chromaScore;
      scoredHct.push({ hct, score });
    }
    scoredHct.sort(compare);
    const chosenColors = [];
    for (let differenceDegrees2 = 90; differenceDegrees2 >= 15; differenceDegrees2--) {
      chosenColors.length = 0;
      for (const { hct } of scoredHct) {
        const duplicateHue = chosenColors.find((chosenHct) => {
          return differenceDegrees(hct.hue, chosenHct.hue) < differenceDegrees2;
        });
        if (!duplicateHue) {
          chosenColors.push(hct);
        }
        if (chosenColors.length >= desired)
          break;
      }
      if (chosenColors.length >= desired)
        break;
    }
    const colors = [];
    if (chosenColors.length === 0) {
      colors.push(fallbackColorARGB);
    }
    for (const chosenHct of chosenColors) {
      colors.push(chosenHct.toInt());
    }
    return colors;
  }
};
Score.TARGET_CHROMA = 48;
Score.WEIGHT_PROPORTION = 0.7;
Score.WEIGHT_CHROMA_ABOVE = 0.3;
Score.WEIGHT_CHROMA_BELOW = 0.1;
Score.CUTOFF_CHROMA = 5;
Score.CUTOFF_EXCITED_PROPORTION = 0.01;

// node_modules/@material/material-color-utilities/utils/string_utils.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
function hexFromArgb(argb) {
  const r2 = redFromArgb(argb);
  const g = greenFromArgb(argb);
  const b = blueFromArgb(argb);
  const outParts = [r2.toString(16), g.toString(16), b.toString(16)];
  for (const [i, part] of outParts.entries()) {
    if (part.length === 1) {
      outParts[i] = "0" + part;
    }
  }
  return "#" + outParts.join("");
}
function argbFromHex(hex2) {
  hex2 = hex2.replace("#", "");
  const isThree = hex2.length === 3;
  const isSix = hex2.length === 6;
  const isEight = hex2.length === 8;
  if (!isThree && !isSix && !isEight) {
    throw new Error("unexpected hex " + hex2);
  }
  let r2 = 0;
  let g = 0;
  let b = 0;
  if (isThree) {
    r2 = parseIntHex(hex2.slice(0, 1).repeat(2));
    g = parseIntHex(hex2.slice(1, 2).repeat(2));
    b = parseIntHex(hex2.slice(2, 3).repeat(2));
  } else if (isSix) {
    r2 = parseIntHex(hex2.slice(0, 2));
    g = parseIntHex(hex2.slice(2, 4));
    b = parseIntHex(hex2.slice(4, 6));
  } else if (isEight) {
    r2 = parseIntHex(hex2.slice(2, 4));
    g = parseIntHex(hex2.slice(4, 6));
    b = parseIntHex(hex2.slice(6, 8));
  }
  return (255 << 24 | (r2 & 255) << 16 | (g & 255) << 8 | b & 255) >>> 0;
}
function parseIntHex(value) {
  return parseInt(value, 16);
}

// node_modules/@material/material-color-utilities/utils/image_utils.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/utils/theme_utils.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/@material/material-color-utilities/index.js
/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// node_modules/culori/src/rgb/parseNumber.js
var parseNumber = (color, len) => {
  if (typeof color !== "number") return;
  if (len === 3) {
    return {
      mode: "rgb",
      r: (color >> 8 & 15 | color >> 4 & 240) / 255,
      g: (color >> 4 & 15 | color & 240) / 255,
      b: (color & 15 | color << 4 & 240) / 255
    };
  }
  if (len === 4) {
    return {
      mode: "rgb",
      r: (color >> 12 & 15 | color >> 8 & 240) / 255,
      g: (color >> 8 & 15 | color >> 4 & 240) / 255,
      b: (color >> 4 & 15 | color & 240) / 255,
      alpha: (color & 15 | color << 4 & 240) / 255
    };
  }
  if (len === 6) {
    return {
      mode: "rgb",
      r: (color >> 16 & 255) / 255,
      g: (color >> 8 & 255) / 255,
      b: (color & 255) / 255
    };
  }
  if (len === 8) {
    return {
      mode: "rgb",
      r: (color >> 24 & 255) / 255,
      g: (color >> 16 & 255) / 255,
      b: (color >> 8 & 255) / 255,
      alpha: (color & 255) / 255
    };
  }
};
var parseNumber_default = parseNumber;

// node_modules/culori/src/colors/named.js
var named = {
  aliceblue: 15792383,
  antiquewhite: 16444375,
  aqua: 65535,
  aquamarine: 8388564,
  azure: 15794175,
  beige: 16119260,
  bisque: 16770244,
  black: 0,
  blanchedalmond: 16772045,
  blue: 255,
  blueviolet: 9055202,
  brown: 10824234,
  burlywood: 14596231,
  cadetblue: 6266528,
  chartreuse: 8388352,
  chocolate: 13789470,
  coral: 16744272,
  cornflowerblue: 6591981,
  cornsilk: 16775388,
  crimson: 14423100,
  cyan: 65535,
  darkblue: 139,
  darkcyan: 35723,
  darkgoldenrod: 12092939,
  darkgray: 11119017,
  darkgreen: 25600,
  darkgrey: 11119017,
  darkkhaki: 12433259,
  darkmagenta: 9109643,
  darkolivegreen: 5597999,
  darkorange: 16747520,
  darkorchid: 10040012,
  darkred: 9109504,
  darksalmon: 15308410,
  darkseagreen: 9419919,
  darkslateblue: 4734347,
  darkslategray: 3100495,
  darkslategrey: 3100495,
  darkturquoise: 52945,
  darkviolet: 9699539,
  deeppink: 16716947,
  deepskyblue: 49151,
  dimgray: 6908265,
  dimgrey: 6908265,
  dodgerblue: 2003199,
  firebrick: 11674146,
  floralwhite: 16775920,
  forestgreen: 2263842,
  fuchsia: 16711935,
  gainsboro: 14474460,
  ghostwhite: 16316671,
  gold: 16766720,
  goldenrod: 14329120,
  gray: 8421504,
  green: 32768,
  greenyellow: 11403055,
  grey: 8421504,
  honeydew: 15794160,
  hotpink: 16738740,
  indianred: 13458524,
  indigo: 4915330,
  ivory: 16777200,
  khaki: 15787660,
  lavender: 15132410,
  lavenderblush: 16773365,
  lawngreen: 8190976,
  lemonchiffon: 16775885,
  lightblue: 11393254,
  lightcoral: 15761536,
  lightcyan: 14745599,
  lightgoldenrodyellow: 16448210,
  lightgray: 13882323,
  lightgreen: 9498256,
  lightgrey: 13882323,
  lightpink: 16758465,
  lightsalmon: 16752762,
  lightseagreen: 2142890,
  lightskyblue: 8900346,
  lightslategray: 7833753,
  lightslategrey: 7833753,
  lightsteelblue: 11584734,
  lightyellow: 16777184,
  lime: 65280,
  limegreen: 3329330,
  linen: 16445670,
  magenta: 16711935,
  maroon: 8388608,
  mediumaquamarine: 6737322,
  mediumblue: 205,
  mediumorchid: 12211667,
  mediumpurple: 9662683,
  mediumseagreen: 3978097,
  mediumslateblue: 8087790,
  mediumspringgreen: 64154,
  mediumturquoise: 4772300,
  mediumvioletred: 13047173,
  midnightblue: 1644912,
  mintcream: 16121850,
  mistyrose: 16770273,
  moccasin: 16770229,
  navajowhite: 16768685,
  navy: 128,
  oldlace: 16643558,
  olive: 8421376,
  olivedrab: 7048739,
  orange: 16753920,
  orangered: 16729344,
  orchid: 14315734,
  palegoldenrod: 15657130,
  palegreen: 10025880,
  paleturquoise: 11529966,
  palevioletred: 14381203,
  papayawhip: 16773077,
  peachpuff: 16767673,
  peru: 13468991,
  pink: 16761035,
  plum: 14524637,
  powderblue: 11591910,
  purple: 8388736,
  // Added in CSS Colors Level 4:
  // https://drafts.csswg.org/css-color/#changes-from-3
  rebeccapurple: 6697881,
  red: 16711680,
  rosybrown: 12357519,
  royalblue: 4286945,
  saddlebrown: 9127187,
  salmon: 16416882,
  sandybrown: 16032864,
  seagreen: 3050327,
  seashell: 16774638,
  sienna: 10506797,
  silver: 12632256,
  skyblue: 8900331,
  slateblue: 6970061,
  slategray: 7372944,
  slategrey: 7372944,
  snow: 16775930,
  springgreen: 65407,
  steelblue: 4620980,
  tan: 13808780,
  teal: 32896,
  thistle: 14204888,
  tomato: 16737095,
  turquoise: 4251856,
  violet: 15631086,
  wheat: 16113331,
  white: 16777215,
  whitesmoke: 16119285,
  yellow: 16776960,
  yellowgreen: 10145074
};
var named_default = named;

// node_modules/culori/src/rgb/parseNamed.js
var parseNamed = (color) => {
  return parseNumber_default(named_default[color.toLowerCase()], 6);
};
var parseNamed_default = parseNamed;

// node_modules/culori/src/rgb/parseHex.js
var hex = /^#?([0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{4}|[0-9a-f]{3})$/i;
var parseHex = (color) => {
  let match;
  return (match = color.match(hex)) ? parseNumber_default(parseInt(match[1], 16), match[1].length) : void 0;
};
var parseHex_default = parseHex;

// node_modules/culori/src/util/regex.js
var num = "([+-]?\\d*\\.?\\d+(?:[eE][+-]?\\d+)?)";
var num_none = `(?:${num}|none)`;
var per = `${num}%`;
var per_none = `(?:${num}%|none)`;
var num_per = `(?:${num}%|${num})`;
var num_per_none = `(?:${num}%|${num}|none)`;
var hue = `(?:${num}(deg|grad|rad|turn)|${num})`;
var hue_none = `(?:${num}(deg|grad|rad|turn)|${num}|none)`;
var c = `\\s*,\\s*`;
var rx_num_per_none = new RegExp("^" + num_per_none + "$");

// node_modules/culori/src/rgb/parseRgbLegacy.js
var rgb_num_old = new RegExp(
  `^rgba?\\(\\s*${num}${c}${num}${c}${num}\\s*(?:,\\s*${num_per}\\s*)?\\)$`
);
var rgb_per_old = new RegExp(
  `^rgba?\\(\\s*${per}${c}${per}${c}${per}\\s*(?:,\\s*${num_per}\\s*)?\\)$`
);
var parseRgbLegacy = (color) => {
  let res = { mode: "rgb" };
  let match;
  if (match = color.match(rgb_num_old)) {
    if (match[1] !== void 0) {
      res.r = match[1] / 255;
    }
    if (match[2] !== void 0) {
      res.g = match[2] / 255;
    }
    if (match[3] !== void 0) {
      res.b = match[3] / 255;
    }
  } else if (match = color.match(rgb_per_old)) {
    if (match[1] !== void 0) {
      res.r = match[1] / 100;
    }
    if (match[2] !== void 0) {
      res.g = match[2] / 100;
    }
    if (match[3] !== void 0) {
      res.b = match[3] / 100;
    }
  } else {
    return void 0;
  }
  if (match[4] !== void 0) {
    res.alpha = Math.max(0, Math.min(1, match[4] / 100));
  } else if (match[5] !== void 0) {
    res.alpha = Math.max(0, Math.min(1, +match[5]));
  }
  return res;
};
var parseRgbLegacy_default = parseRgbLegacy;

// node_modules/culori/src/_prepare.js
var prepare = (color, mode) => color === void 0 ? void 0 : typeof color !== "object" ? parse_default(color) : color.mode !== void 0 ? color : mode ? { ...color, mode } : void 0;
var prepare_default = prepare;

// node_modules/culori/src/converter.js
var converter = (target_mode = "rgb") => (color) => (color = prepare_default(color, target_mode)) !== void 0 ? (
  // if the color's mode corresponds to our target mode
  color.mode === target_mode ? (
    // then just return the color
    color
  ) : (
    // otherwise check to see if we have a dedicated
    // converter for the target mode
    converters[color.mode][target_mode] ? (
      // and return its result...
      converters[color.mode][target_mode](color)
    ) : (
      // ...otherwise pass through RGB as an intermediary step.
      // if the target mode is RGB...
      target_mode === "rgb" ? (
        // just return the RGB
        converters[color.mode].rgb(color)
      ) : (
        // otherwise convert color.mode -> RGB -> target_mode
        converters.rgb[target_mode](converters[color.mode].rgb(color))
      )
    )
  )
) : void 0;
var converter_default = converter;

// node_modules/culori/src/modes.js
var converters = {};
var modes = {};
var parsers = [];
var colorProfiles = {};
var identity = (v) => v;
var useMode = (definition29) => {
  converters[definition29.mode] = {
    ...converters[definition29.mode],
    ...definition29.toMode
  };
  Object.keys(definition29.fromMode || {}).forEach((k4) => {
    if (!converters[k4]) {
      converters[k4] = {};
    }
    converters[k4][definition29.mode] = definition29.fromMode[k4];
  });
  if (!definition29.ranges) {
    definition29.ranges = {};
  }
  if (!definition29.difference) {
    definition29.difference = {};
  }
  definition29.channels.forEach((channel) => {
    if (definition29.ranges[channel] === void 0) {
      definition29.ranges[channel] = [0, 1];
    }
    if (!definition29.interpolate[channel]) {
      throw new Error(`Missing interpolator for: ${channel}`);
    }
    if (typeof definition29.interpolate[channel] === "function") {
      definition29.interpolate[channel] = {
        use: definition29.interpolate[channel]
      };
    }
    if (!definition29.interpolate[channel].fixup) {
      definition29.interpolate[channel].fixup = identity;
    }
  });
  modes[definition29.mode] = definition29;
  (definition29.parse || []).forEach((parser) => {
    useParser(parser, definition29.mode);
  });
  return converter_default(definition29.mode);
};
var getMode = (mode) => modes[mode];
var useParser = (parser, mode) => {
  if (typeof parser === "string") {
    if (!mode) {
      throw new Error(`'mode' required when 'parser' is a string`);
    }
    colorProfiles[parser] = mode;
  } else if (typeof parser === "function") {
    if (parsers.indexOf(parser) < 0) {
      parsers.push(parser);
    }
  }
};

// node_modules/culori/src/parse.js
var IdentStartCodePoint = /[^\x00-\x7F]|[a-zA-Z_]/;
var IdentCodePoint = /[^\x00-\x7F]|[-\w]/;
var Tok = {
  Function: "function",
  Ident: "ident",
  Number: "number",
  Percentage: "percentage",
  ParenClose: ")",
  None: "none",
  Hue: "hue",
  Alpha: "alpha"
};
var _i = 0;
function is_num(chars) {
  let ch = chars[_i];
  let ch1 = chars[_i + 1];
  if (ch === "-" || ch === "+") {
    return /\d/.test(ch1) || ch1 === "." && /\d/.test(chars[_i + 2]);
  }
  if (ch === ".") {
    return /\d/.test(ch1);
  }
  return /\d/.test(ch);
}
function is_ident(chars) {
  if (_i >= chars.length) {
    return false;
  }
  let ch = chars[_i];
  if (IdentStartCodePoint.test(ch)) {
    return true;
  }
  if (ch === "-") {
    if (chars.length - _i < 2) {
      return false;
    }
    let ch1 = chars[_i + 1];
    if (ch1 === "-" || IdentStartCodePoint.test(ch1)) {
      return true;
    }
    return false;
  }
  return false;
}
var huenits = {
  deg: 1,
  rad: 180 / Math.PI,
  grad: 9 / 10,
  turn: 360
};
function num2(chars) {
  let value = "";
  if (chars[_i] === "-" || chars[_i] === "+") {
    value += chars[_i++];
  }
  value += digits(chars);
  if (chars[_i] === "." && /\d/.test(chars[_i + 1])) {
    value += chars[_i++] + digits(chars);
  }
  if (chars[_i] === "e" || chars[_i] === "E") {
    if ((chars[_i + 1] === "-" || chars[_i + 1] === "+") && /\d/.test(chars[_i + 2])) {
      value += chars[_i++] + chars[_i++] + digits(chars);
    } else if (/\d/.test(chars[_i + 1])) {
      value += chars[_i++] + digits(chars);
    }
  }
  if (is_ident(chars)) {
    let id = ident(chars);
    if (id === "deg" || id === "rad" || id === "turn" || id === "grad") {
      return { type: Tok.Hue, value: value * huenits[id] };
    }
    return void 0;
  }
  if (chars[_i] === "%") {
    _i++;
    return { type: Tok.Percentage, value: +value };
  }
  return { type: Tok.Number, value: +value };
}
function digits(chars) {
  let v = "";
  while (/\d/.test(chars[_i])) {
    v += chars[_i++];
  }
  return v;
}
function ident(chars) {
  let v = "";
  while (_i < chars.length && IdentCodePoint.test(chars[_i])) {
    v += chars[_i++];
  }
  return v;
}
function identlike(chars) {
  let v = ident(chars);
  if (chars[_i] === "(") {
    _i++;
    return { type: Tok.Function, value: v };
  }
  if (v === "none") {
    return { type: Tok.None, value: void 0 };
  }
  return { type: Tok.Ident, value: v };
}
function tokenize(str = "") {
  let chars = str.trim();
  let tokens = [];
  let ch;
  _i = 0;
  while (_i < chars.length) {
    ch = chars[_i++];
    if (ch === "\n" || ch === "	" || ch === " ") {
      while (_i < chars.length && (chars[_i] === "\n" || chars[_i] === "	" || chars[_i] === " ")) {
        _i++;
      }
      continue;
    }
    if (ch === ",") {
      return void 0;
    }
    if (ch === ")") {
      tokens.push({ type: Tok.ParenClose });
      continue;
    }
    if (ch === "+") {
      _i--;
      if (is_num(chars)) {
        tokens.push(num2(chars));
        continue;
      }
      return void 0;
    }
    if (ch === "-") {
      _i--;
      if (is_num(chars)) {
        tokens.push(num2(chars));
        continue;
      }
      if (is_ident(chars)) {
        tokens.push({ type: Tok.Ident, value: ident(chars) });
        continue;
      }
      return void 0;
    }
    if (ch === ".") {
      _i--;
      if (is_num(chars)) {
        tokens.push(num2(chars));
        continue;
      }
      return void 0;
    }
    if (ch === "/") {
      while (_i < chars.length && (chars[_i] === "\n" || chars[_i] === "	" || chars[_i] === " ")) {
        _i++;
      }
      let alpha;
      if (is_num(chars)) {
        alpha = num2(chars);
        if (alpha.type !== Tok.Hue) {
          tokens.push({ type: Tok.Alpha, value: alpha });
          continue;
        }
      }
      if (is_ident(chars)) {
        if (ident(chars) === "none") {
          tokens.push({
            type: Tok.Alpha,
            value: { type: Tok.None, value: void 0 }
          });
          continue;
        }
      }
      return void 0;
    }
    if (/\d/.test(ch)) {
      _i--;
      tokens.push(num2(chars));
      continue;
    }
    if (IdentStartCodePoint.test(ch)) {
      _i--;
      tokens.push(identlike(chars));
      continue;
    }
    return void 0;
  }
  return tokens;
}
function parseColorSyntax(tokens) {
  tokens._i = 0;
  let token = tokens[tokens._i++];
  if (!token || token.type !== Tok.Function || token.value !== "color") {
    return void 0;
  }
  token = tokens[tokens._i++];
  if (token.type !== Tok.Ident) {
    return void 0;
  }
  const mode = colorProfiles[token.value];
  if (!mode) {
    return void 0;
  }
  const res = { mode };
  const coords = consumeCoords(tokens, false);
  if (!coords) {
    return void 0;
  }
  const channels = getMode(mode).channels;
  for (let ii = 0, c2, ch; ii < channels.length; ii++) {
    c2 = coords[ii];
    ch = channels[ii];
    if (c2.type !== Tok.None) {
      res[ch] = c2.type === Tok.Number ? c2.value : c2.value / 100;
      if (ch === "alpha") {
        res[ch] = Math.max(0, Math.min(1, res[ch]));
      }
    }
  }
  return res;
}
function consumeCoords(tokens, includeHue) {
  const coords = [];
  let token;
  while (tokens._i < tokens.length) {
    token = tokens[tokens._i++];
    if (token.type === Tok.None || token.type === Tok.Number || token.type === Tok.Alpha || token.type === Tok.Percentage || includeHue && token.type === Tok.Hue) {
      coords.push(token);
      continue;
    }
    if (token.type === Tok.ParenClose) {
      if (tokens._i < tokens.length) {
        return void 0;
      }
      continue;
    }
    return void 0;
  }
  if (coords.length < 3 || coords.length > 4) {
    return void 0;
  }
  if (coords.length === 4) {
    if (coords[3].type !== Tok.Alpha) {
      return void 0;
    }
    coords[3] = coords[3].value;
  }
  if (coords.length === 3) {
    coords.push({ type: Tok.None, value: void 0 });
  }
  return coords.every((c2) => c2.type !== Tok.Alpha) ? coords : void 0;
}
function parseModernSyntax(tokens, includeHue) {
  tokens._i = 0;
  let token = tokens[tokens._i++];
  if (!token || token.type !== Tok.Function) {
    return void 0;
  }
  let coords = consumeCoords(tokens, includeHue);
  if (!coords) {
    return void 0;
  }
  coords.unshift(token.value);
  return coords;
}
var parse = (color) => {
  if (typeof color !== "string") {
    return void 0;
  }
  const tokens = tokenize(color);
  const parsed = tokens ? parseModernSyntax(tokens, true) : void 0;
  let result = void 0;
  let i = 0;
  let len = parsers.length;
  while (i < len) {
    if ((result = parsers[i++](color, parsed)) !== void 0) {
      return result;
    }
  }
  return tokens ? parseColorSyntax(tokens) : void 0;
};
var parse_default = parse;

// node_modules/culori/src/rgb/parseRgb.js
function parseRgb(color, parsed) {
  if (!parsed || parsed[0] !== "rgb" && parsed[0] !== "rgba") {
    return void 0;
  }
  const res = { mode: "rgb" };
  const [, r2, g, b, alpha] = parsed;
  if (r2.type === Tok.Hue || g.type === Tok.Hue || b.type === Tok.Hue) {
    return void 0;
  }
  if (r2.type !== Tok.None) {
    res.r = r2.type === Tok.Number ? r2.value / 255 : r2.value / 100;
  }
  if (g.type !== Tok.None) {
    res.g = g.type === Tok.Number ? g.value / 255 : g.value / 100;
  }
  if (b.type !== Tok.None) {
    res.b = b.type === Tok.Number ? b.value / 255 : b.value / 100;
  }
  if (alpha.type !== Tok.None) {
    res.alpha = Math.min(
      1,
      Math.max(
        0,
        alpha.type === Tok.Number ? alpha.value : alpha.value / 100
      )
    );
  }
  return res;
}
var parseRgb_default = parseRgb;

// node_modules/culori/src/rgb/parseTransparent.js
var parseTransparent = (c2) => c2 === "transparent" ? { mode: "rgb", r: 0, g: 0, b: 0, alpha: 0 } : void 0;
var parseTransparent_default = parseTransparent;

// node_modules/culori/src/interpolate/lerp.js
var lerp2 = (a, b, t) => a + t * (b - a);

// node_modules/culori/src/interpolate/piecewise.js
var get_classes = (arr) => {
  let classes = [];
  for (let i = 0; i < arr.length - 1; i++) {
    let a = arr[i];
    let b = arr[i + 1];
    if (a === void 0 && b === void 0) {
      classes.push(void 0);
    } else if (a !== void 0 && b !== void 0) {
      classes.push([a, b]);
    } else {
      classes.push(a !== void 0 ? [a, a] : [b, b]);
    }
  }
  return classes;
};
var interpolatorPiecewise = (interpolator) => (arr) => {
  let classes = get_classes(arr);
  return (t) => {
    let cls = t * classes.length;
    let idx = t >= 1 ? classes.length - 1 : Math.max(Math.floor(cls), 0);
    let pair = classes[idx];
    return pair === void 0 ? void 0 : interpolator(pair[0], pair[1], cls - idx);
  };
};

// node_modules/culori/src/interpolate/linear.js
var interpolatorLinear = interpolatorPiecewise(lerp2);

// node_modules/culori/src/fixup/alpha.js
var fixupAlpha = (arr) => {
  let some_defined = false;
  let res = arr.map((v) => {
    if (v !== void 0) {
      some_defined = true;
      return v;
    }
    return 1;
  });
  return some_defined ? res : arr;
};

// node_modules/culori/src/rgb/definition.js
var definition = {
  mode: "rgb",
  channels: ["r", "g", "b", "alpha"],
  parse: [
    parseRgb_default,
    parseHex_default,
    parseRgbLegacy_default,
    parseNamed_default,
    parseTransparent_default,
    "srgb"
  ],
  serialize: "srgb",
  interpolate: {
    r: interpolatorLinear,
    g: interpolatorLinear,
    b: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  },
  gamut: true,
  white: { r: 1, g: 1, b: 1 },
  black: { r: 0, g: 0, b: 0 }
};
var definition_default = definition;

// node_modules/culori/src/a98/convertA98ToXyz65.js
var linearize = (v = 0) => Math.pow(Math.abs(v), 563 / 256) * Math.sign(v);
var convertA98ToXyz65 = (a982) => {
  let r2 = linearize(a982.r);
  let g = linearize(a982.g);
  let b = linearize(a982.b);
  let res = {
    mode: "xyz65",
    x: 0.5766690429101305 * r2 + 0.1855582379065463 * g + 0.1882286462349947 * b,
    y: 0.297344975250536 * r2 + 0.6273635662554661 * g + 0.0752914584939979 * b,
    z: 0.0270313613864123 * r2 + 0.0706888525358272 * g + 0.9913375368376386 * b
  };
  if (a982.alpha !== void 0) {
    res.alpha = a982.alpha;
  }
  return res;
};
var convertA98ToXyz65_default = convertA98ToXyz65;

// node_modules/culori/src/a98/convertXyz65ToA98.js
var gamma = (v) => Math.pow(Math.abs(v), 256 / 563) * Math.sign(v);
var convertXyz65ToA98 = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let res = {
    mode: "a98",
    r: gamma(
      x * 2.0415879038107465 - y * 0.5650069742788597 - 0.3447313507783297 * z
    ),
    g: gamma(
      x * -0.9692436362808798 + y * 1.8759675015077206 + 0.0415550574071756 * z
    ),
    b: gamma(
      x * 0.0134442806320312 - y * 0.1183623922310184 + 1.0151749943912058 * z
    )
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz65ToA98_default = convertXyz65ToA98;

// node_modules/culori/src/lrgb/convertRgbToLrgb.js
var fn = (c2 = 0) => {
  const abs2 = Math.abs(c2);
  if (abs2 <= 0.04045) {
    return c2 / 12.92;
  }
  return (Math.sign(c2) || 1) * Math.pow((abs2 + 0.055) / 1.055, 2.4);
};
var convertRgbToLrgb = ({ r: r2, g, b, alpha }) => {
  let res = {
    mode: "lrgb",
    r: fn(r2),
    g: fn(g),
    b: fn(b)
  };
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertRgbToLrgb_default = convertRgbToLrgb;

// node_modules/culori/src/xyz65/convertRgbToXyz65.js
var convertRgbToXyz65 = (rgb4) => {
  let { r: r2, g, b, alpha } = convertRgbToLrgb_default(rgb4);
  let res = {
    mode: "xyz65",
    x: 0.4123907992659593 * r2 + 0.357584339383878 * g + 0.1804807884018343 * b,
    y: 0.2126390058715102 * r2 + 0.715168678767756 * g + 0.0721923153607337 * b,
    z: 0.0193308187155918 * r2 + 0.119194779794626 * g + 0.9505321522496607 * b
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertRgbToXyz65_default = convertRgbToXyz65;

// node_modules/culori/src/lrgb/convertLrgbToRgb.js
var fn2 = (c2 = 0) => {
  const abs2 = Math.abs(c2);
  if (abs2 > 31308e-7) {
    return (Math.sign(c2) || 1) * (1.055 * Math.pow(abs2, 1 / 2.4) - 0.055);
  }
  return c2 * 12.92;
};
var convertLrgbToRgb = ({ r: r2, g, b, alpha }, mode = "rgb") => {
  let res = {
    mode,
    r: fn2(r2),
    g: fn2(g),
    b: fn2(b)
  };
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertLrgbToRgb_default = convertLrgbToRgb;

// node_modules/culori/src/xyz65/convertXyz65ToRgb.js
var convertXyz65ToRgb = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let res = convertLrgbToRgb_default({
    r: x * 3.2409699419045226 - y * 1.537383177570094 - 0.4986107602930034 * z,
    g: x * -0.9692436362808796 + y * 1.8759675015077204 + 0.0415550574071756 * z,
    b: x * 0.0556300796969936 - y * 0.2039769588889765 + 1.0569715142428784 * z
  });
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz65ToRgb_default = convertXyz65ToRgb;

// node_modules/culori/src/a98/definition.js
var definition2 = {
  ...definition_default,
  mode: "a98",
  parse: ["a98-rgb"],
  serialize: "a98-rgb",
  fromMode: {
    rgb: (color) => convertXyz65ToA98_default(convertRgbToXyz65_default(color)),
    xyz65: convertXyz65ToA98_default
  },
  toMode: {
    rgb: (color) => convertXyz65ToRgb_default(convertA98ToXyz65_default(color)),
    xyz65: convertA98ToXyz65_default
  }
};
var definition_default2 = definition2;

// node_modules/culori/src/util/normalizeHue.js
var normalizeHue = (hue3) => (hue3 = hue3 % 360) < 0 ? hue3 + 360 : hue3;
var normalizeHue_default = normalizeHue;

// node_modules/culori/src/fixup/hue.js
var hue2 = (hues, fn5) => {
  return hues.map((hue3, idx, arr) => {
    if (hue3 === void 0) {
      return hue3;
    }
    let normalized = normalizeHue_default(hue3);
    if (idx === 0 || hues[idx - 1] === void 0) {
      return normalized;
    }
    return fn5(normalized - normalizeHue_default(arr[idx - 1]));
  }).reduce((acc, curr) => {
    if (!acc.length || curr === void 0 || acc[acc.length - 1] === void 0) {
      acc.push(curr);
      return acc;
    }
    acc.push(curr + acc[acc.length - 1]);
    return acc;
  }, []);
};
var fixupHueShorter = (arr) => hue2(arr, (d) => Math.abs(d) <= 180 ? d : d - 360 * Math.sign(d));

// node_modules/culori/src/cubehelix/constants.js
var M = [-0.14861, 1.78277, -0.29227, -0.90649, 1.97294, 0];
var degToRad = Math.PI / 180;
var radToDeg = 180 / Math.PI;

// node_modules/culori/src/cubehelix/convertRgbToCubehelix.js
var DE = M[3] * M[4];
var BE = M[1] * M[4];
var BCAD = M[1] * M[2] - M[0] * M[3];
var convertRgbToCubehelix = ({ r: r2, g, b, alpha }) => {
  if (r2 === void 0) r2 = 0;
  if (g === void 0) g = 0;
  if (b === void 0) b = 0;
  let l = (BCAD * b + r2 * DE - g * BE) / (BCAD + DE - BE);
  let x = b - l;
  let y = (M[4] * (g - l) - M[2] * x) / M[3];
  let res = {
    mode: "cubehelix",
    l,
    s: l === 0 || l === 1 ? void 0 : Math.sqrt(x * x + y * y) / (M[4] * l * (1 - l))
  };
  if (res.s) res.h = Math.atan2(y, x) * radToDeg - 120;
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertRgbToCubehelix_default = convertRgbToCubehelix;

// node_modules/culori/src/cubehelix/convertCubehelixToRgb.js
var convertCubehelixToRgb = ({ h, s, l, alpha }) => {
  let res = { mode: "rgb" };
  h = (h === void 0 ? 0 : h + 120) * degToRad;
  if (l === void 0) l = 0;
  let amp = s === void 0 ? 0 : s * l * (1 - l);
  let cosh = Math.cos(h);
  let sinh = Math.sin(h);
  res.r = l + amp * (M[0] * cosh + M[1] * sinh);
  res.g = l + amp * (M[2] * cosh + M[3] * sinh);
  res.b = l + amp * (M[4] * cosh + M[5] * sinh);
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertCubehelixToRgb_default = convertCubehelixToRgb;

// node_modules/culori/src/difference.js
var differenceHueSaturation = (std, smp) => {
  if (std.h === void 0 || smp.h === void 0 || !std.s || !smp.s) {
    return 0;
  }
  let std_h = normalizeHue_default(std.h);
  let smp_h = normalizeHue_default(smp.h);
  let dH = Math.sin((smp_h - std_h + 360) / 2 * Math.PI / 180);
  return 2 * Math.sqrt(std.s * smp.s) * dH;
};
var differenceHueNaive = (std, smp) => {
  if (std.h === void 0 || smp.h === void 0) {
    return 0;
  }
  let std_h = normalizeHue_default(std.h);
  let smp_h = normalizeHue_default(smp.h);
  if (Math.abs(smp_h - std_h) > 180) {
    return std_h - (smp_h - 360 * Math.sign(smp_h - std_h));
  }
  return smp_h - std_h;
};
var differenceHueChroma = (std, smp) => {
  if (std.h === void 0 || smp.h === void 0 || !std.c || !smp.c) {
    return 0;
  }
  let std_h = normalizeHue_default(std.h);
  let smp_h = normalizeHue_default(smp.h);
  let dH = Math.sin((smp_h - std_h + 360) / 2 * Math.PI / 180);
  return 2 * Math.sqrt(std.c * smp.c) * dH;
};
var differenceEuclidean = (mode = "rgb", weights = [1, 1, 1, 0]) => {
  let def = getMode(mode);
  let channels = def.channels;
  let diffs = def.difference;
  let conv = converter_default(mode);
  return (std, smp) => {
    let ConvStd = conv(std);
    let ConvSmp = conv(smp);
    return Math.sqrt(
      channels.reduce((sum, k4, idx) => {
        let delta = diffs[k4] ? diffs[k4](ConvStd, ConvSmp) : ConvStd[k4] - ConvSmp[k4];
        return sum + (weights[idx] || 0) * Math.pow(isNaN(delta) ? 0 : delta, 2);
      }, 0)
    );
  };
};

// node_modules/culori/src/average.js
var averageAngle = (val) => {
  let sum = val.reduce(
    (sum2, val2) => {
      if (val2 !== void 0) {
        let rad = val2 * Math.PI / 180;
        sum2.sin += Math.sin(rad);
        sum2.cos += Math.cos(rad);
      }
      return sum2;
    },
    { sin: 0, cos: 0 }
  );
  let angle = Math.atan2(sum.sin, sum.cos) * 180 / Math.PI;
  return angle < 0 ? 360 + angle : angle;
};

// node_modules/culori/src/cubehelix/definition.js
var definition3 = {
  mode: "cubehelix",
  channels: ["h", "s", "l", "alpha"],
  parse: ["--cubehelix"],
  serialize: "--cubehelix",
  ranges: {
    h: [0, 360],
    s: [0, 4.614],
    l: [0, 1]
  },
  fromMode: {
    rgb: convertRgbToCubehelix_default
  },
  toMode: {
    rgb: convertCubehelixToRgb_default
  },
  interpolate: {
    h: {
      use: interpolatorLinear,
      fixup: fixupHueShorter
    },
    s: interpolatorLinear,
    l: interpolatorLinear,
    alpha: {
      use: interpolatorLinear,
      fixup: fixupAlpha
    }
  },
  difference: {
    h: differenceHueSaturation
  },
  average: {
    h: averageAngle
  }
};
var definition_default3 = definition3;

// node_modules/culori/src/lch/convertLabToLch.js
var convertLabToLch = ({ l, a, b, alpha }, mode = "lch") => {
  if (a === void 0) a = 0;
  if (b === void 0) b = 0;
  let c2 = Math.sqrt(a * a + b * b);
  let res = { mode, l, c: c2 };
  if (c2) res.h = normalizeHue_default(Math.atan2(b, a) * 180 / Math.PI);
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertLabToLch_default = convertLabToLch;

// node_modules/culori/src/lch/convertLchToLab.js
var convertLchToLab = ({ l, c: c2, h, alpha }, mode = "lab") => {
  if (h === void 0) h = 0;
  let res = {
    mode,
    l,
    a: c2 ? c2 * Math.cos(h / 180 * Math.PI) : 0,
    b: c2 ? c2 * Math.sin(h / 180 * Math.PI) : 0
  };
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertLchToLab_default = convertLchToLab;

// node_modules/culori/src/xyz65/constants.js
var k = Math.pow(29, 3) / Math.pow(3, 3);
var e = Math.pow(6, 3) / Math.pow(29, 3);

// node_modules/culori/src/constants.js
var D50 = {
  X: 0.3457 / 0.3585,
  Y: 1,
  Z: (1 - 0.3457 - 0.3585) / 0.3585
};
var D65 = {
  X: 0.3127 / 0.329,
  Y: 1,
  Z: (1 - 0.3127 - 0.329) / 0.329
};
var k2 = Math.pow(29, 3) / Math.pow(3, 3);
var e2 = Math.pow(6, 3) / Math.pow(29, 3);

// node_modules/culori/src/lab65/convertLab65ToXyz65.js
var fn3 = (v) => Math.pow(v, 3) > e ? Math.pow(v, 3) : (116 * v - 16) / k;
var convertLab65ToXyz65 = ({ l, a, b, alpha }) => {
  if (l === void 0) l = 0;
  if (a === void 0) a = 0;
  if (b === void 0) b = 0;
  let fy = (l + 16) / 116;
  let fx = a / 500 + fy;
  let fz = fy - b / 200;
  let res = {
    mode: "xyz65",
    x: fn3(fx) * D65.X,
    y: fn3(fy) * D65.Y,
    z: fn3(fz) * D65.Z
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertLab65ToXyz65_default = convertLab65ToXyz65;

// node_modules/culori/src/lab65/convertLab65ToRgb.js
var convertLab65ToRgb = (lab2) => convertXyz65ToRgb_default(convertLab65ToXyz65_default(lab2));
var convertLab65ToRgb_default = convertLab65ToRgb;

// node_modules/culori/src/lab65/convertXyz65ToLab65.js
var f = (value) => value > e ? Math.cbrt(value) : (k * value + 16) / 116;
var convertXyz65ToLab65 = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let f0 = f(x / D65.X);
  let f1 = f(y / D65.Y);
  let f22 = f(z / D65.Z);
  let res = {
    mode: "lab65",
    l: 116 * f1 - 16,
    a: 500 * (f0 - f1),
    b: 200 * (f1 - f22)
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz65ToLab65_default = convertXyz65ToLab65;

// node_modules/culori/src/lab65/convertRgbToLab65.js
var convertRgbToLab65 = (rgb4) => {
  let res = convertXyz65ToLab65_default(convertRgbToXyz65_default(rgb4));
  if (rgb4.r === rgb4.b && rgb4.b === rgb4.g) {
    res.a = res.b = 0;
  }
  return res;
};
var convertRgbToLab65_default = convertRgbToLab65;

// node_modules/culori/src/dlch/constants.js
var kE = 1;
var kCH = 1;
var \u03B8 = 26 / 180 * Math.PI;
var cos\u03B8 = Math.cos(\u03B8);
var sin\u03B8 = Math.sin(\u03B8);
var factor = 100 / Math.log(139 / 100);

// node_modules/culori/src/dlch/convertDlchToLab65.js
var convertDlchToLab65 = ({ l, c: c2, h, alpha }) => {
  if (l === void 0) l = 0;
  if (c2 === void 0) c2 = 0;
  if (h === void 0) h = 0;
  let res = {
    mode: "lab65",
    l: (Math.exp(l * kE / factor) - 1) / 39e-4
  };
  let G = (Math.exp(0.0435 * c2 * kCH * kE) - 1) / 0.075;
  let e4 = G * Math.cos(h / 180 * Math.PI - \u03B8);
  let f3 = G * Math.sin(h / 180 * Math.PI - \u03B8);
  res.a = e4 * cos\u03B8 - f3 / 0.83 * sin\u03B8;
  res.b = e4 * sin\u03B8 + f3 / 0.83 * cos\u03B8;
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertDlchToLab65_default = convertDlchToLab65;

// node_modules/culori/src/dlch/convertLab65ToDlch.js
var convertLab65ToDlch = ({ l, a, b, alpha }) => {
  if (l === void 0) l = 0;
  if (a === void 0) a = 0;
  if (b === void 0) b = 0;
  let e4 = a * cos\u03B8 + b * sin\u03B8;
  let f3 = 0.83 * (b * cos\u03B8 - a * sin\u03B8);
  let G = Math.sqrt(e4 * e4 + f3 * f3);
  let res = {
    mode: "dlch",
    l: factor / kE * Math.log(1 + 39e-4 * l),
    c: Math.log(1 + 0.075 * G) / (0.0435 * kCH * kE)
  };
  if (res.c) {
    res.h = normalizeHue_default((Math.atan2(f3, e4) + \u03B8) / Math.PI * 180);
  }
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertLab65ToDlch_default = convertLab65ToDlch;

// node_modules/culori/src/dlab/definition.js
var convertDlabToLab65 = (c2) => convertDlchToLab65_default(convertLabToLch_default(c2, "dlch"));
var convertLab65ToDlab = (c2) => convertLchToLab_default(convertLab65ToDlch_default(c2), "dlab");
var definition4 = {
  mode: "dlab",
  parse: ["--din99o-lab"],
  serialize: "--din99o-lab",
  toMode: {
    lab65: convertDlabToLab65,
    rgb: (c2) => convertLab65ToRgb_default(convertDlabToLab65(c2))
  },
  fromMode: {
    lab65: convertLab65ToDlab,
    rgb: (c2) => convertLab65ToDlab(convertRgbToLab65_default(c2))
  },
  channels: ["l", "a", "b", "alpha"],
  ranges: {
    l: [0, 100],
    a: [-40.09, 45.501],
    b: [-40.469, 44.344]
  },
  interpolate: {
    l: interpolatorLinear,
    a: interpolatorLinear,
    b: interpolatorLinear,
    alpha: {
      use: interpolatorLinear,
      fixup: fixupAlpha
    }
  }
};
var definition_default4 = definition4;

// node_modules/culori/src/dlch/definition.js
var definition5 = {
  mode: "dlch",
  parse: ["--din99o-lch"],
  serialize: "--din99o-lch",
  toMode: {
    lab65: convertDlchToLab65_default,
    dlab: (c2) => convertLchToLab_default(c2, "dlab"),
    rgb: (c2) => convertLab65ToRgb_default(convertDlchToLab65_default(c2))
  },
  fromMode: {
    lab65: convertLab65ToDlch_default,
    dlab: (c2) => convertLabToLch_default(c2, "dlch"),
    rgb: (c2) => convertLab65ToDlch_default(convertRgbToLab65_default(c2))
  },
  channels: ["l", "c", "h", "alpha"],
  ranges: {
    l: [0, 100],
    c: [0, 51.484],
    h: [0, 360]
  },
  interpolate: {
    l: interpolatorLinear,
    c: interpolatorLinear,
    h: {
      use: interpolatorLinear,
      fixup: fixupHueShorter
    },
    alpha: {
      use: interpolatorLinear,
      fixup: fixupAlpha
    }
  },
  difference: {
    h: differenceHueChroma
  },
  average: {
    h: averageAngle
  }
};
var definition_default5 = definition5;

// node_modules/culori/src/hsi/convertHsiToRgb.js
function convertHsiToRgb({ h, s, i, alpha }) {
  h = normalizeHue_default(h !== void 0 ? h : 0);
  if (s === void 0) s = 0;
  if (i === void 0) i = 0;
  let f3 = Math.abs(h / 60 % 2 - 1);
  let res;
  switch (Math.floor(h / 60)) {
    case 0:
      res = {
        r: i * (1 + s * (3 / (2 - f3) - 1)),
        g: i * (1 + s * (3 * (1 - f3) / (2 - f3) - 1)),
        b: i * (1 - s)
      };
      break;
    case 1:
      res = {
        r: i * (1 + s * (3 * (1 - f3) / (2 - f3) - 1)),
        g: i * (1 + s * (3 / (2 - f3) - 1)),
        b: i * (1 - s)
      };
      break;
    case 2:
      res = {
        r: i * (1 - s),
        g: i * (1 + s * (3 / (2 - f3) - 1)),
        b: i * (1 + s * (3 * (1 - f3) / (2 - f3) - 1))
      };
      break;
    case 3:
      res = {
        r: i * (1 - s),
        g: i * (1 + s * (3 * (1 - f3) / (2 - f3) - 1)),
        b: i * (1 + s * (3 / (2 - f3) - 1))
      };
      break;
    case 4:
      res = {
        r: i * (1 + s * (3 * (1 - f3) / (2 - f3) - 1)),
        g: i * (1 - s),
        b: i * (1 + s * (3 / (2 - f3) - 1))
      };
      break;
    case 5:
      res = {
        r: i * (1 + s * (3 / (2 - f3) - 1)),
        g: i * (1 - s),
        b: i * (1 + s * (3 * (1 - f3) / (2 - f3) - 1))
      };
      break;
    default:
      res = { r: i * (1 - s), g: i * (1 - s), b: i * (1 - s) };
  }
  res.mode = "rgb";
  if (alpha !== void 0) res.alpha = alpha;
  return res;
}

// node_modules/culori/src/hsi/convertRgbToHsi.js
function convertRgbToHsi({ r: r2, g, b, alpha }) {
  if (r2 === void 0) r2 = 0;
  if (g === void 0) g = 0;
  if (b === void 0) b = 0;
  let M3 = Math.max(r2, g, b), m = Math.min(r2, g, b);
  let res = {
    mode: "hsi",
    s: r2 + g + b === 0 ? 0 : 1 - 3 * m / (r2 + g + b),
    i: (r2 + g + b) / 3
  };
  if (M3 - m !== 0)
    res.h = (M3 === r2 ? (g - b) / (M3 - m) + (g < b) * 6 : M3 === g ? (b - r2) / (M3 - m) + 2 : (r2 - g) / (M3 - m) + 4) * 60;
  if (alpha !== void 0) res.alpha = alpha;
  return res;
}

// node_modules/culori/src/hsi/definition.js
var definition6 = {
  mode: "hsi",
  toMode: {
    rgb: convertHsiToRgb
  },
  parse: ["--hsi"],
  serialize: "--hsi",
  fromMode: {
    rgb: convertRgbToHsi
  },
  channels: ["h", "s", "i", "alpha"],
  ranges: {
    h: [0, 360]
  },
  gamut: "rgb",
  interpolate: {
    h: { use: interpolatorLinear, fixup: fixupHueShorter },
    s: interpolatorLinear,
    i: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  },
  difference: {
    h: differenceHueSaturation
  },
  average: {
    h: averageAngle
  }
};
var definition_default6 = definition6;

// node_modules/culori/src/hsl/convertHslToRgb.js
function convertHslToRgb({ h, s, l, alpha }) {
  h = normalizeHue_default(h !== void 0 ? h : 0);
  if (s === void 0) s = 0;
  if (l === void 0) l = 0;
  let m1 = l + s * (l < 0.5 ? l : 1 - l);
  let m2 = m1 - (m1 - l) * 2 * Math.abs(h / 60 % 2 - 1);
  let res;
  switch (Math.floor(h / 60)) {
    case 0:
      res = { r: m1, g: m2, b: 2 * l - m1 };
      break;
    case 1:
      res = { r: m2, g: m1, b: 2 * l - m1 };
      break;
    case 2:
      res = { r: 2 * l - m1, g: m1, b: m2 };
      break;
    case 3:
      res = { r: 2 * l - m1, g: m2, b: m1 };
      break;
    case 4:
      res = { r: m2, g: 2 * l - m1, b: m1 };
      break;
    case 5:
      res = { r: m1, g: 2 * l - m1, b: m2 };
      break;
    default:
      res = { r: 2 * l - m1, g: 2 * l - m1, b: 2 * l - m1 };
  }
  res.mode = "rgb";
  if (alpha !== void 0) res.alpha = alpha;
  return res;
}

// node_modules/culori/src/hsl/convertRgbToHsl.js
function convertRgbToHsl({ r: r2, g, b, alpha }) {
  if (r2 === void 0) r2 = 0;
  if (g === void 0) g = 0;
  if (b === void 0) b = 0;
  let M3 = Math.max(r2, g, b), m = Math.min(r2, g, b);
  let res = {
    mode: "hsl",
    s: M3 === m ? 0 : (M3 - m) / (1 - Math.abs(M3 + m - 1)),
    l: 0.5 * (M3 + m)
  };
  if (M3 - m !== 0)
    res.h = (M3 === r2 ? (g - b) / (M3 - m) + (g < b) * 6 : M3 === g ? (b - r2) / (M3 - m) + 2 : (r2 - g) / (M3 - m) + 4) * 60;
  if (alpha !== void 0) res.alpha = alpha;
  return res;
}

// node_modules/culori/src/util/hue.js
var hueToDeg = (val, unit) => {
  switch (unit) {
    case "deg":
      return +val;
    case "rad":
      return val / Math.PI * 180;
    case "grad":
      return val / 10 * 9;
    case "turn":
      return val * 360;
  }
};
var hue_default = hueToDeg;

// node_modules/culori/src/hsl/parseHslLegacy.js
var hsl_old = new RegExp(
  `^hsla?\\(\\s*${hue}${c}${per}${c}${per}\\s*(?:,\\s*${num_per}\\s*)?\\)$`
);
var parseHslLegacy = (color) => {
  let match = color.match(hsl_old);
  if (!match) return;
  let res = { mode: "hsl" };
  if (match[3] !== void 0) {
    res.h = +match[3];
  } else if (match[1] !== void 0 && match[2] !== void 0) {
    res.h = hue_default(match[1], match[2]);
  }
  if (match[4] !== void 0) {
    res.s = Math.min(Math.max(0, match[4] / 100), 1);
  }
  if (match[5] !== void 0) {
    res.l = Math.min(Math.max(0, match[5] / 100), 1);
  }
  if (match[6] !== void 0) {
    res.alpha = Math.max(0, Math.min(1, match[6] / 100));
  } else if (match[7] !== void 0) {
    res.alpha = Math.max(0, Math.min(1, +match[7]));
  }
  return res;
};
var parseHslLegacy_default = parseHslLegacy;

// node_modules/culori/src/hsl/parseHsl.js
function parseHsl(color, parsed) {
  if (!parsed || parsed[0] !== "hsl" && parsed[0] !== "hsla") {
    return void 0;
  }
  const res = { mode: "hsl" };
  const [, h, s, l, alpha] = parsed;
  if (h.type !== Tok.None) {
    if (h.type === Tok.Percentage) {
      return void 0;
    }
    res.h = h.value;
  }
  if (s.type !== Tok.None) {
    if (s.type === Tok.Hue) {
      return void 0;
    }
    res.s = s.value / 100;
  }
  if (l.type !== Tok.None) {
    if (l.type === Tok.Hue) {
      return void 0;
    }
    res.l = l.value / 100;
  }
  if (alpha.type !== Tok.None) {
    res.alpha = Math.min(
      1,
      Math.max(
        0,
        alpha.type === Tok.Number ? alpha.value : alpha.value / 100
      )
    );
  }
  return res;
}
var parseHsl_default = parseHsl;

// node_modules/culori/src/hsl/definition.js
var definition7 = {
  mode: "hsl",
  toMode: {
    rgb: convertHslToRgb
  },
  fromMode: {
    rgb: convertRgbToHsl
  },
  channels: ["h", "s", "l", "alpha"],
  ranges: {
    h: [0, 360]
  },
  gamut: "rgb",
  parse: [parseHsl_default, parseHslLegacy_default],
  serialize: (c2) => `hsl(${c2.h !== void 0 ? c2.h : "none"} ${c2.s !== void 0 ? c2.s * 100 + "%" : "none"} ${c2.l !== void 0 ? c2.l * 100 + "%" : "none"}${c2.alpha < 1 ? ` / ${c2.alpha}` : ""})`,
  interpolate: {
    h: { use: interpolatorLinear, fixup: fixupHueShorter },
    s: interpolatorLinear,
    l: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  },
  difference: {
    h: differenceHueSaturation
  },
  average: {
    h: averageAngle
  }
};
var definition_default7 = definition7;

// node_modules/culori/src/hsv/convertHsvToRgb.js
function convertHsvToRgb({ h, s, v, alpha }) {
  h = normalizeHue_default(h !== void 0 ? h : 0);
  if (s === void 0) s = 0;
  if (v === void 0) v = 0;
  let f3 = Math.abs(h / 60 % 2 - 1);
  let res;
  switch (Math.floor(h / 60)) {
    case 0:
      res = { r: v, g: v * (1 - s * f3), b: v * (1 - s) };
      break;
    case 1:
      res = { r: v * (1 - s * f3), g: v, b: v * (1 - s) };
      break;
    case 2:
      res = { r: v * (1 - s), g: v, b: v * (1 - s * f3) };
      break;
    case 3:
      res = { r: v * (1 - s), g: v * (1 - s * f3), b: v };
      break;
    case 4:
      res = { r: v * (1 - s * f3), g: v * (1 - s), b: v };
      break;
    case 5:
      res = { r: v, g: v * (1 - s), b: v * (1 - s * f3) };
      break;
    default:
      res = { r: v * (1 - s), g: v * (1 - s), b: v * (1 - s) };
  }
  res.mode = "rgb";
  if (alpha !== void 0) res.alpha = alpha;
  return res;
}

// node_modules/culori/src/hsv/convertRgbToHsv.js
function convertRgbToHsv({ r: r2, g, b, alpha }) {
  if (r2 === void 0) r2 = 0;
  if (g === void 0) g = 0;
  if (b === void 0) b = 0;
  let M3 = Math.max(r2, g, b), m = Math.min(r2, g, b);
  let res = {
    mode: "hsv",
    s: M3 === 0 ? 0 : 1 - m / M3,
    v: M3
  };
  if (M3 - m !== 0)
    res.h = (M3 === r2 ? (g - b) / (M3 - m) + (g < b) * 6 : M3 === g ? (b - r2) / (M3 - m) + 2 : (r2 - g) / (M3 - m) + 4) * 60;
  if (alpha !== void 0) res.alpha = alpha;
  return res;
}

// node_modules/culori/src/hsv/definition.js
var definition8 = {
  mode: "hsv",
  toMode: {
    rgb: convertHsvToRgb
  },
  parse: ["--hsv"],
  serialize: "--hsv",
  fromMode: {
    rgb: convertRgbToHsv
  },
  channels: ["h", "s", "v", "alpha"],
  ranges: {
    h: [0, 360]
  },
  gamut: "rgb",
  interpolate: {
    h: { use: interpolatorLinear, fixup: fixupHueShorter },
    s: interpolatorLinear,
    v: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  },
  difference: {
    h: differenceHueSaturation
  },
  average: {
    h: averageAngle
  }
};
var definition_default8 = definition8;

// node_modules/culori/src/hwb/convertHwbToRgb.js
function convertHwbToRgb({ h, w, b, alpha }) {
  if (w === void 0) w = 0;
  if (b === void 0) b = 0;
  if (w + b > 1) {
    let s = w + b;
    w /= s;
    b /= s;
  }
  return convertHsvToRgb({
    h,
    s: b === 1 ? 1 : 1 - w / (1 - b),
    v: 1 - b,
    alpha
  });
}

// node_modules/culori/src/hwb/convertRgbToHwb.js
function convertRgbToHwb(rgba) {
  let hsv2 = convertRgbToHsv(rgba);
  if (hsv2 === void 0) return void 0;
  let s = hsv2.s !== void 0 ? hsv2.s : 0;
  let v = hsv2.v !== void 0 ? hsv2.v : 0;
  let res = {
    mode: "hwb",
    w: (1 - s) * v,
    b: 1 - v
  };
  if (hsv2.h !== void 0) res.h = hsv2.h;
  if (hsv2.alpha !== void 0) res.alpha = hsv2.alpha;
  return res;
}

// node_modules/culori/src/hwb/parseHwb.js
function ParseHwb(color, parsed) {
  if (!parsed || parsed[0] !== "hwb") {
    return void 0;
  }
  const res = { mode: "hwb" };
  const [, h, w, b, alpha] = parsed;
  if (h.type !== Tok.None) {
    if (h.type === Tok.Percentage) {
      return void 0;
    }
    res.h = h.value;
  }
  if (w.type !== Tok.None) {
    if (w.type === Tok.Hue) {
      return void 0;
    }
    res.w = w.value / 100;
  }
  if (b.type !== Tok.None) {
    if (b.type === Tok.Hue) {
      return void 0;
    }
    res.b = b.value / 100;
  }
  if (alpha.type !== Tok.None) {
    res.alpha = Math.min(
      1,
      Math.max(
        0,
        alpha.type === Tok.Number ? alpha.value : alpha.value / 100
      )
    );
  }
  return res;
}
var parseHwb_default = ParseHwb;

// node_modules/culori/src/hwb/definition.js
var definition9 = {
  mode: "hwb",
  toMode: {
    rgb: convertHwbToRgb
  },
  fromMode: {
    rgb: convertRgbToHwb
  },
  channels: ["h", "w", "b", "alpha"],
  ranges: {
    h: [0, 360]
  },
  gamut: "rgb",
  parse: [parseHwb_default],
  serialize: (c2) => `hwb(${c2.h !== void 0 ? c2.h : "none"} ${c2.w !== void 0 ? c2.w * 100 + "%" : "none"} ${c2.b !== void 0 ? c2.b * 100 + "%" : "none"}${c2.alpha < 1 ? ` / ${c2.alpha}` : ""})`,
  interpolate: {
    h: { use: interpolatorLinear, fixup: fixupHueShorter },
    w: interpolatorLinear,
    b: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  },
  difference: {
    h: differenceHueNaive
  },
  average: {
    h: averageAngle
  }
};
var definition_default9 = definition9;

// node_modules/culori/src/hdr/constants.js
var YW = 203;

// node_modules/culori/src/hdr/transfer.js
var M1 = 0.1593017578125;
var M2 = 78.84375;
var C1 = 0.8359375;
var C2 = 18.8515625;
var C3 = 18.6875;
function transferPqDecode(v) {
  if (v < 0) return 0;
  const c2 = Math.pow(v, 1 / M2);
  return 1e4 * Math.pow(Math.max(0, c2 - C1) / (C2 - C3 * c2), 1 / M1);
}
function transferPqEncode(v) {
  if (v < 0) return 0;
  const c2 = Math.pow(v / 1e4, M1);
  return Math.pow((C1 + C2 * c2) / (1 + C3 * c2), M2);
}

// node_modules/culori/src/itp/convertItpToXyz65.js
var toRel = (c2) => Math.max(c2 / YW, 0);
var convertItpToXyz65 = ({ i, t, p: p4, alpha }) => {
  if (i === void 0) i = 0;
  if (t === void 0) t = 0;
  if (p4 === void 0) p4 = 0;
  const l = transferPqDecode(
    i + 0.008609037037932761 * t + 0.11102962500302593 * p4
  );
  const m = transferPqDecode(
    i - 0.00860903703793275 * t - 0.11102962500302599 * p4
  );
  const s = transferPqDecode(
    i + 0.5600313357106791 * t - 0.32062717498731885 * p4
  );
  const res = {
    mode: "xyz65",
    x: toRel(
      2.070152218389422 * l - 1.3263473389671556 * m + 0.2066510476294051 * s
    ),
    y: toRel(
      0.3647385209748074 * l + 0.680566024947227 * m - 0.0453045459220346 * s
    ),
    z: toRel(
      -0.049747207535812 * l - 0.0492609666966138 * m + 1.1880659249923042 * s
    )
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertItpToXyz65_default = convertItpToXyz65;

// node_modules/culori/src/itp/convertXyz65ToItp.js
var toAbs = (c2 = 0) => Math.max(c2 * YW, 0);
var convertXyz65ToItp = ({ x, y, z, alpha }) => {
  const absX = toAbs(x);
  const absY = toAbs(y);
  const absZ = toAbs(z);
  const l = transferPqEncode(
    0.3592832590121217 * absX + 0.6976051147779502 * absY - 0.0358915932320289 * absZ
  );
  const m = transferPqEncode(
    -0.1920808463704995 * absX + 1.1004767970374323 * absY + 0.0753748658519118 * absZ
  );
  const s = transferPqEncode(
    0.0070797844607477 * absX + 0.0748396662186366 * absY + 0.8433265453898765 * absZ
  );
  const i = 0.5 * l + 0.5 * m;
  const t = 1.61376953125 * l - 3.323486328125 * m + 1.709716796875 * s;
  const p4 = 4.378173828125 * l - 4.24560546875 * m - 0.132568359375 * s;
  const res = { mode: "itp", i, t, p: p4 };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz65ToItp_default = convertXyz65ToItp;

// node_modules/culori/src/itp/definition.js
var definition10 = {
  mode: "itp",
  channels: ["i", "t", "p", "alpha"],
  parse: ["--ictcp"],
  serialize: "--ictcp",
  toMode: {
    xyz65: convertItpToXyz65_default,
    rgb: (color) => convertXyz65ToRgb_default(convertItpToXyz65_default(color))
  },
  fromMode: {
    xyz65: convertXyz65ToItp_default,
    rgb: (color) => convertXyz65ToItp_default(convertRgbToXyz65_default(color))
  },
  ranges: {
    i: [0, 0.581],
    t: [-0.369, 0.272],
    p: [-0.164, 0.331]
  },
  interpolate: {
    i: interpolatorLinear,
    t: interpolatorLinear,
    p: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  }
};
var definition_default10 = definition10;

// node_modules/culori/src/jab/convertXyz65ToJab.js
var p = 134.03437499999998;
var d0 = 16295499532821565e-27;
var jabPqEncode = (v) => {
  if (v < 0) return 0;
  let vn3 = Math.pow(v / 1e4, M1);
  return Math.pow((C1 + C2 * vn3) / (1 + C3 * vn3), p);
};
var abs = (v = 0) => Math.max(v * 203, 0);
var convertXyz65ToJab = ({ x, y, z, alpha }) => {
  x = abs(x);
  y = abs(y);
  z = abs(z);
  let xp = 1.15 * x - 0.15 * z;
  let yp = 0.66 * y + 0.34 * x;
  let l = jabPqEncode(0.41478972 * xp + 0.579999 * yp + 0.014648 * z);
  let m = jabPqEncode(-0.20151 * xp + 1.120649 * yp + 0.0531008 * z);
  let s = jabPqEncode(-0.0166008 * xp + 0.2648 * yp + 0.6684799 * z);
  let i = (l + m) / 2;
  let res = {
    mode: "jab",
    j: 0.44 * i / (1 - 0.56 * i) - d0,
    a: 3.524 * l - 4.066708 * m + 0.542708 * s,
    b: 0.199076 * l + 1.096799 * m - 1.295875 * s
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz65ToJab_default = convertXyz65ToJab;

// node_modules/culori/src/jab/convertJabToXyz65.js
var p2 = 134.03437499999998;
var d02 = 16295499532821565e-27;
var jabPqDecode = (v) => {
  if (v < 0) return 0;
  let vp = Math.pow(v, 1 / p2);
  return 1e4 * Math.pow((C1 - vp) / (C3 * vp - C2), 1 / M1);
};
var rel = (v) => v / 203;
var convertJabToXyz65 = ({ j, a, b, alpha }) => {
  if (j === void 0) j = 0;
  if (a === void 0) a = 0;
  if (b === void 0) b = 0;
  let i = (j + d02) / (0.44 + 0.56 * (j + d02));
  let l = jabPqDecode(i + 0.13860504 * a + 0.058047316 * b);
  let m = jabPqDecode(i - 0.13860504 * a - 0.058047316 * b);
  let s = jabPqDecode(i - 0.096019242 * a - 0.8118919 * b);
  let res = {
    mode: "xyz65",
    x: rel(
      1.661373024652174 * l - 0.914523081304348 * m + 0.23136208173913045 * s
    ),
    y: rel(
      -0.3250758611844533 * l + 1.571847026732543 * m - 0.21825383453227928 * s
    ),
    z: rel(-0.090982811 * l - 0.31272829 * m + 1.5227666 * s)
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertJabToXyz65_default = convertJabToXyz65;

// node_modules/culori/src/jab/convertRgbToJab.js
var convertRgbToJab = (rgb4) => {
  let res = convertXyz65ToJab_default(convertRgbToXyz65_default(rgb4));
  if (rgb4.r === rgb4.b && rgb4.b === rgb4.g) {
    res.a = res.b = 0;
  }
  return res;
};
var convertRgbToJab_default = convertRgbToJab;

// node_modules/culori/src/jab/convertJabToRgb.js
var convertJabToRgb = (color) => convertXyz65ToRgb_default(convertJabToXyz65_default(color));
var convertJabToRgb_default = convertJabToRgb;

// node_modules/culori/src/jab/definition.js
var definition11 = {
  mode: "jab",
  channels: ["j", "a", "b", "alpha"],
  parse: ["--jzazbz"],
  serialize: "--jzazbz",
  fromMode: {
    rgb: convertRgbToJab_default,
    xyz65: convertXyz65ToJab_default
  },
  toMode: {
    rgb: convertJabToRgb_default,
    xyz65: convertJabToXyz65_default
  },
  ranges: {
    j: [0, 0.222],
    a: [-0.109, 0.129],
    b: [-0.185, 0.134]
  },
  interpolate: {
    j: interpolatorLinear,
    a: interpolatorLinear,
    b: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  }
};
var definition_default11 = definition11;

// node_modules/culori/src/jch/convertJabToJch.js
var convertJabToJch = ({ j, a, b, alpha }) => {
  if (a === void 0) a = 0;
  if (b === void 0) b = 0;
  let c2 = Math.sqrt(a * a + b * b);
  let res = {
    mode: "jch",
    j,
    c: c2
  };
  if (c2) {
    res.h = normalizeHue_default(Math.atan2(b, a) * 180 / Math.PI);
  }
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertJabToJch_default = convertJabToJch;

// node_modules/culori/src/jch/convertJchToJab.js
var convertJchToJab = ({ j, c: c2, h, alpha }) => {
  if (h === void 0) h = 0;
  let res = {
    mode: "jab",
    j,
    a: c2 ? c2 * Math.cos(h / 180 * Math.PI) : 0,
    b: c2 ? c2 * Math.sin(h / 180 * Math.PI) : 0
  };
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertJchToJab_default = convertJchToJab;

// node_modules/culori/src/jch/definition.js
var definition12 = {
  mode: "jch",
  parse: ["--jzczhz"],
  serialize: "--jzczhz",
  toMode: {
    jab: convertJchToJab_default,
    rgb: (c2) => convertJabToRgb_default(convertJchToJab_default(c2))
  },
  fromMode: {
    rgb: (c2) => convertJabToJch_default(convertRgbToJab_default(c2)),
    jab: convertJabToJch_default
  },
  channels: ["j", "c", "h", "alpha"],
  ranges: {
    j: [0, 0.221],
    c: [0, 0.19],
    h: [0, 360]
  },
  interpolate: {
    h: { use: interpolatorLinear, fixup: fixupHueShorter },
    c: interpolatorLinear,
    j: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  },
  difference: {
    h: differenceHueChroma
  },
  average: {
    h: averageAngle
  }
};
var definition_default12 = definition12;

// node_modules/culori/src/xyz50/constants.js
var k3 = Math.pow(29, 3) / Math.pow(3, 3);
var e3 = Math.pow(6, 3) / Math.pow(29, 3);

// node_modules/culori/src/lab/convertLabToXyz50.js
var fn4 = (v) => Math.pow(v, 3) > e3 ? Math.pow(v, 3) : (116 * v - 16) / k3;
var convertLabToXyz50 = ({ l, a, b, alpha }) => {
  if (l === void 0) l = 0;
  if (a === void 0) a = 0;
  if (b === void 0) b = 0;
  let fy = (l + 16) / 116;
  let fx = a / 500 + fy;
  let fz = fy - b / 200;
  let res = {
    mode: "xyz50",
    x: fn4(fx) * D50.X,
    y: fn4(fy) * D50.Y,
    z: fn4(fz) * D50.Z
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertLabToXyz50_default = convertLabToXyz50;

// node_modules/culori/src/xyz50/convertXyz50ToRgb.js
var convertXyz50ToRgb = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let res = convertLrgbToRgb_default({
    r: x * 3.1341359569958707 - y * 1.6173863321612538 - 0.4906619460083532 * z,
    g: x * -0.978795502912089 + y * 1.916254567259524 + 0.03344273116131949 * z,
    b: x * 0.07195537988411677 - y * 0.2289768264158322 + 1.405386058324125 * z
  });
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz50ToRgb_default = convertXyz50ToRgb;

// node_modules/culori/src/lab/convertLabToRgb.js
var convertLabToRgb = (lab2) => convertXyz50ToRgb_default(convertLabToXyz50_default(lab2));
var convertLabToRgb_default = convertLabToRgb;

// node_modules/culori/src/xyz50/convertRgbToXyz50.js
var convertRgbToXyz50 = (rgb4) => {
  let { r: r2, g, b, alpha } = convertRgbToLrgb_default(rgb4);
  let res = {
    mode: "xyz50",
    x: 0.436065742824811 * r2 + 0.3851514688337912 * g + 0.14307845442264197 * b,
    y: 0.22249319175623702 * r2 + 0.7168870538238823 * g + 0.06061979053616537 * b,
    z: 0.013923904500943465 * r2 + 0.09708128566574634 * g + 0.7140993584005155 * b
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertRgbToXyz50_default = convertRgbToXyz50;

// node_modules/culori/src/lab/convertXyz50ToLab.js
var f2 = (value) => value > e3 ? Math.cbrt(value) : (k3 * value + 16) / 116;
var convertXyz50ToLab = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let f0 = f2(x / D50.X);
  let f1 = f2(y / D50.Y);
  let f22 = f2(z / D50.Z);
  let res = {
    mode: "lab",
    l: 116 * f1 - 16,
    a: 500 * (f0 - f1),
    b: 200 * (f1 - f22)
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz50ToLab_default = convertXyz50ToLab;

// node_modules/culori/src/lab/convertRgbToLab.js
var convertRgbToLab = (rgb4) => {
  let res = convertXyz50ToLab_default(convertRgbToXyz50_default(rgb4));
  if (rgb4.r === rgb4.b && rgb4.b === rgb4.g) {
    res.a = res.b = 0;
  }
  return res;
};
var convertRgbToLab_default = convertRgbToLab;

// node_modules/culori/src/lab/parseLab.js
function parseLab(color, parsed) {
  if (!parsed || parsed[0] !== "lab") {
    return void 0;
  }
  const res = { mode: "lab" };
  const [, l, a, b, alpha] = parsed;
  if (l.type === Tok.Hue || a.type === Tok.Hue || b.type === Tok.Hue) {
    return void 0;
  }
  if (l.type !== Tok.None) {
    res.l = Math.min(Math.max(0, l.value), 100);
  }
  if (a.type !== Tok.None) {
    res.a = a.type === Tok.Number ? a.value : a.value * 125 / 100;
  }
  if (b.type !== Tok.None) {
    res.b = b.type === Tok.Number ? b.value : b.value * 125 / 100;
  }
  if (alpha.type !== Tok.None) {
    res.alpha = Math.min(
      1,
      Math.max(
        0,
        alpha.type === Tok.Number ? alpha.value : alpha.value / 100
      )
    );
  }
  return res;
}
var parseLab_default = parseLab;

// node_modules/culori/src/lab/definition.js
var definition13 = {
  mode: "lab",
  toMode: {
    xyz50: convertLabToXyz50_default,
    rgb: convertLabToRgb_default
  },
  fromMode: {
    xyz50: convertXyz50ToLab_default,
    rgb: convertRgbToLab_default
  },
  channels: ["l", "a", "b", "alpha"],
  ranges: {
    l: [0, 100],
    a: [-125, 125],
    b: [-125, 125]
  },
  parse: [parseLab_default],
  serialize: (c2) => `lab(${c2.l !== void 0 ? c2.l : "none"} ${c2.a !== void 0 ? c2.a : "none"} ${c2.b !== void 0 ? c2.b : "none"}${c2.alpha < 1 ? ` / ${c2.alpha}` : ""})`,
  interpolate: {
    l: interpolatorLinear,
    a: interpolatorLinear,
    b: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  }
};
var definition_default13 = definition13;

// node_modules/culori/src/lab65/definition.js
var definition14 = {
  ...definition_default13,
  mode: "lab65",
  parse: ["--lab-d65"],
  serialize: "--lab-d65",
  toMode: {
    xyz65: convertLab65ToXyz65_default,
    rgb: convertLab65ToRgb_default
  },
  fromMode: {
    xyz65: convertXyz65ToLab65_default,
    rgb: convertRgbToLab65_default
  },
  ranges: {
    l: [0, 100],
    a: [-125, 125],
    b: [-125, 125]
  }
};
var definition_default14 = definition14;

// node_modules/culori/src/lch/parseLch.js
function parseLch(color, parsed) {
  if (!parsed || parsed[0] !== "lch") {
    return void 0;
  }
  const res = { mode: "lch" };
  const [, l, c2, h, alpha] = parsed;
  if (l.type !== Tok.None) {
    if (l.type === Tok.Hue) {
      return void 0;
    }
    res.l = Math.min(Math.max(0, l.value), 100);
  }
  if (c2.type !== Tok.None) {
    res.c = Math.max(
      0,
      c2.type === Tok.Number ? c2.value : c2.value * 150 / 100
    );
  }
  if (h.type !== Tok.None) {
    if (h.type === Tok.Percentage) {
      return void 0;
    }
    res.h = h.value;
  }
  if (alpha.type !== Tok.None) {
    res.alpha = Math.min(
      1,
      Math.max(
        0,
        alpha.type === Tok.Number ? alpha.value : alpha.value / 100
      )
    );
  }
  return res;
}
var parseLch_default = parseLch;

// node_modules/culori/src/lch/definition.js
var definition15 = {
  mode: "lch",
  toMode: {
    lab: convertLchToLab_default,
    rgb: (c2) => convertLabToRgb_default(convertLchToLab_default(c2))
  },
  fromMode: {
    rgb: (c2) => convertLabToLch_default(convertRgbToLab_default(c2)),
    lab: convertLabToLch_default
  },
  channels: ["l", "c", "h", "alpha"],
  ranges: {
    l: [0, 100],
    c: [0, 150],
    h: [0, 360]
  },
  parse: [parseLch_default],
  serialize: (c2) => `lch(${c2.l !== void 0 ? c2.l : "none"} ${c2.c !== void 0 ? c2.c : "none"} ${c2.h !== void 0 ? c2.h : "none"}${c2.alpha < 1 ? ` / ${c2.alpha}` : ""})`,
  interpolate: {
    h: { use: interpolatorLinear, fixup: fixupHueShorter },
    c: interpolatorLinear,
    l: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  },
  difference: {
    h: differenceHueChroma
  },
  average: {
    h: averageAngle
  }
};
var definition_default15 = definition15;

// node_modules/culori/src/lch65/definition.js
var definition16 = {
  ...definition_default15,
  mode: "lch65",
  parse: ["--lch-d65"],
  serialize: "--lch-d65",
  toMode: {
    lab65: (c2) => convertLchToLab_default(c2, "lab65"),
    rgb: (c2) => convertLab65ToRgb_default(convertLchToLab_default(c2, "lab65"))
  },
  fromMode: {
    rgb: (c2) => convertLabToLch_default(convertRgbToLab65_default(c2), "lch65"),
    lab65: (c2) => convertLabToLch_default(c2, "lch65")
  },
  ranges: {
    l: [0, 100],
    c: [0, 150],
    h: [0, 360]
  }
};
var definition_default16 = definition16;

// node_modules/culori/src/lchuv/convertLuvToLchuv.js
var convertLuvToLchuv = ({ l, u, v, alpha }) => {
  if (u === void 0) u = 0;
  if (v === void 0) v = 0;
  let c2 = Math.sqrt(u * u + v * v);
  let res = {
    mode: "lchuv",
    l,
    c: c2
  };
  if (c2) {
    res.h = normalizeHue_default(Math.atan2(v, u) * 180 / Math.PI);
  }
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertLuvToLchuv_default = convertLuvToLchuv;

// node_modules/culori/src/lchuv/convertLchuvToLuv.js
var convertLchuvToLuv = ({ l, c: c2, h, alpha }) => {
  if (h === void 0) h = 0;
  let res = {
    mode: "luv",
    l,
    u: c2 ? c2 * Math.cos(h / 180 * Math.PI) : 0,
    v: c2 ? c2 * Math.sin(h / 180 * Math.PI) : 0
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertLchuvToLuv_default = convertLchuvToLuv;

// node_modules/culori/src/luv/convertXyz50ToLuv.js
var u_fn = (x, y, z) => 4 * x / (x + 15 * y + 3 * z);
var v_fn = (x, y, z) => 9 * y / (x + 15 * y + 3 * z);
var un = u_fn(D50.X, D50.Y, D50.Z);
var vn = v_fn(D50.X, D50.Y, D50.Z);
var l_fn = (value) => value <= e3 ? k3 * value : 116 * Math.cbrt(value) - 16;
var convertXyz50ToLuv = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let l = l_fn(y / D50.Y);
  let u = u_fn(x, y, z);
  let v = v_fn(x, y, z);
  if (!isFinite(u) || !isFinite(v)) {
    l = u = v = 0;
  } else {
    u = 13 * l * (u - un);
    v = 13 * l * (v - vn);
  }
  let res = {
    mode: "luv",
    l,
    u,
    v
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz50ToLuv_default = convertXyz50ToLuv;

// node_modules/culori/src/luv/convertLuvToXyz50.js
var u_fn2 = (x, y, z) => 4 * x / (x + 15 * y + 3 * z);
var v_fn2 = (x, y, z) => 9 * y / (x + 15 * y + 3 * z);
var un2 = u_fn2(D50.X, D50.Y, D50.Z);
var vn2 = v_fn2(D50.X, D50.Y, D50.Z);
var convertLuvToXyz50 = ({ l, u, v, alpha }) => {
  if (l === void 0) l = 0;
  if (l === 0) {
    return { mode: "xyz50", x: 0, y: 0, z: 0 };
  }
  if (u === void 0) u = 0;
  if (v === void 0) v = 0;
  let up = u / (13 * l) + un2;
  let vp = v / (13 * l) + vn2;
  let y = D50.Y * (l <= 8 ? l / k3 : Math.pow((l + 16) / 116, 3));
  let x = y * (9 * up) / (4 * vp);
  let z = y * (12 - 3 * up - 20 * vp) / (4 * vp);
  let res = { mode: "xyz50", x, y, z };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertLuvToXyz50_default = convertLuvToXyz50;

// node_modules/culori/src/lchuv/definition.js
var convertRgbToLchuv = (rgb4) => convertLuvToLchuv_default(convertXyz50ToLuv_default(convertRgbToXyz50_default(rgb4)));
var convertLchuvToRgb = (lchuv2) => convertXyz50ToRgb_default(convertLuvToXyz50_default(convertLchuvToLuv_default(lchuv2)));
var definition17 = {
  mode: "lchuv",
  toMode: {
    luv: convertLchuvToLuv_default,
    rgb: convertLchuvToRgb
  },
  fromMode: {
    rgb: convertRgbToLchuv,
    luv: convertLuvToLchuv_default
  },
  channels: ["l", "c", "h", "alpha"],
  parse: ["--lchuv"],
  serialize: "--lchuv",
  ranges: {
    l: [0, 100],
    c: [0, 176.956],
    h: [0, 360]
  },
  interpolate: {
    h: { use: interpolatorLinear, fixup: fixupHueShorter },
    c: interpolatorLinear,
    l: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  },
  difference: {
    h: differenceHueChroma
  },
  average: {
    h: averageAngle
  }
};
var definition_default17 = definition17;

// node_modules/culori/src/lrgb/definition.js
var definition18 = {
  ...definition_default,
  mode: "lrgb",
  toMode: {
    rgb: convertLrgbToRgb_default
  },
  fromMode: {
    rgb: convertRgbToLrgb_default
  },
  parse: ["srgb-linear"],
  serialize: "srgb-linear"
};
var definition_default18 = definition18;

// node_modules/culori/src/luv/definition.js
var definition19 = {
  mode: "luv",
  toMode: {
    xyz50: convertLuvToXyz50_default,
    rgb: (luv2) => convertXyz50ToRgb_default(convertLuvToXyz50_default(luv2))
  },
  fromMode: {
    xyz50: convertXyz50ToLuv_default,
    rgb: (rgb4) => convertXyz50ToLuv_default(convertRgbToXyz50_default(rgb4))
  },
  channels: ["l", "u", "v", "alpha"],
  parse: ["--luv"],
  serialize: "--luv",
  ranges: {
    l: [0, 100],
    u: [-84.936, 175.042],
    v: [-125.882, 87.243]
  },
  interpolate: {
    l: interpolatorLinear,
    u: interpolatorLinear,
    v: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  }
};
var definition_default19 = definition19;

// node_modules/culori/src/oklab/convertLrgbToOklab.js
var convertLrgbToOklab = ({ r: r2, g, b, alpha }) => {
  if (r2 === void 0) r2 = 0;
  if (g === void 0) g = 0;
  if (b === void 0) b = 0;
  let L = Math.cbrt(
    0.412221469470763 * r2 + 0.5363325372617348 * g + 0.0514459932675022 * b
  );
  let M3 = Math.cbrt(
    0.2119034958178252 * r2 + 0.6806995506452344 * g + 0.1073969535369406 * b
  );
  let S = Math.cbrt(
    0.0883024591900564 * r2 + 0.2817188391361215 * g + 0.6299787016738222 * b
  );
  let res = {
    mode: "oklab",
    l: 0.210454268309314 * L + 0.7936177747023054 * M3 - 0.0040720430116193 * S,
    a: 1.9779985324311684 * L - 2.42859224204858 * M3 + 0.450593709617411 * S,
    b: 0.0259040424655478 * L + 0.7827717124575296 * M3 - 0.8086757549230774 * S
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertLrgbToOklab_default = convertLrgbToOklab;

// node_modules/culori/src/oklab/convertRgbToOklab.js
var convertRgbToOklab = (rgb4) => {
  let res = convertLrgbToOklab_default(convertRgbToLrgb_default(rgb4));
  if (rgb4.r === rgb4.b && rgb4.b === rgb4.g) {
    res.a = res.b = 0;
  }
  return res;
};
var convertRgbToOklab_default = convertRgbToOklab;

// node_modules/culori/src/oklab/convertOklabToLrgb.js
var convertOklabToLrgb = ({ l, a, b, alpha }) => {
  if (l === void 0) l = 0;
  if (a === void 0) a = 0;
  if (b === void 0) b = 0;
  let L = Math.pow(l + 0.3963377773761749 * a + 0.2158037573099136 * b, 3);
  let M3 = Math.pow(l - 0.1055613458156586 * a - 0.0638541728258133 * b, 3);
  let S = Math.pow(l - 0.0894841775298119 * a - 1.2914855480194092 * b, 3);
  let res = {
    mode: "lrgb",
    r: 4.076741636075957 * L - 3.3077115392580616 * M3 + 0.2309699031821044 * S,
    g: -1.2684379732850317 * L + 2.6097573492876887 * M3 - 0.3413193760026573 * S,
    b: -0.0041960761386756 * L - 0.7034186179359362 * M3 + 1.7076146940746117 * S
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertOklabToLrgb_default = convertOklabToLrgb;

// node_modules/culori/src/oklab/convertOklabToRgb.js
var convertOklabToRgb = (c2) => convertLrgbToRgb_default(convertOklabToLrgb_default(c2));
var convertOklabToRgb_default = convertOklabToRgb;

// node_modules/culori/src/okhsl/helpers.js
function toe(x) {
  const k_1 = 0.206;
  const k_2 = 0.03;
  const k_3 = (1 + k_1) / (1 + k_2);
  return 0.5 * (k_3 * x - k_1 + Math.sqrt((k_3 * x - k_1) * (k_3 * x - k_1) + 4 * k_2 * k_3 * x));
}
function toe_inv(x) {
  const k_1 = 0.206;
  const k_2 = 0.03;
  const k_3 = (1 + k_1) / (1 + k_2);
  return (x * x + k_1 * x) / (k_3 * (x + k_2));
}
function compute_max_saturation(a, b) {
  let k0, k1, k22, k32, k4, wl, wm, ws;
  if (-1.88170328 * a - 0.80936493 * b > 1) {
    k0 = 1.19086277;
    k1 = 1.76576728;
    k22 = 0.59662641;
    k32 = 0.75515197;
    k4 = 0.56771245;
    wl = 4.0767416621;
    wm = -3.3077115913;
    ws = 0.2309699292;
  } else if (1.81444104 * a - 1.19445276 * b > 1) {
    k0 = 0.73956515;
    k1 = -0.45954404;
    k22 = 0.08285427;
    k32 = 0.1254107;
    k4 = 0.14503204;
    wl = -1.2684380046;
    wm = 2.6097574011;
    ws = -0.3413193965;
  } else {
    k0 = 1.35733652;
    k1 = -915799e-8;
    k22 = -1.1513021;
    k32 = -0.50559606;
    k4 = 692167e-8;
    wl = -0.0041960863;
    wm = -0.7034186147;
    ws = 1.707614701;
  }
  let S = k0 + k1 * a + k22 * b + k32 * a * a + k4 * a * b;
  let k_l = 0.3963377774 * a + 0.2158037573 * b;
  let k_m = -0.1055613458 * a - 0.0638541728 * b;
  let k_s = -0.0894841775 * a - 1.291485548 * b;
  {
    let l_ = 1 + S * k_l;
    let m_ = 1 + S * k_m;
    let s_ = 1 + S * k_s;
    let l = l_ * l_ * l_;
    let m = m_ * m_ * m_;
    let s = s_ * s_ * s_;
    let l_dS = 3 * k_l * l_ * l_;
    let m_dS = 3 * k_m * m_ * m_;
    let s_dS = 3 * k_s * s_ * s_;
    let l_dS2 = 6 * k_l * k_l * l_;
    let m_dS2 = 6 * k_m * k_m * m_;
    let s_dS2 = 6 * k_s * k_s * s_;
    let f3 = wl * l + wm * m + ws * s;
    let f1 = wl * l_dS + wm * m_dS + ws * s_dS;
    let f22 = wl * l_dS2 + wm * m_dS2 + ws * s_dS2;
    S = S - f3 * f1 / (f1 * f1 - 0.5 * f3 * f22);
  }
  return S;
}
function find_cusp(a, b) {
  let S_cusp = compute_max_saturation(a, b);
  let rgb4 = convertOklabToLrgb_default({ l: 1, a: S_cusp * a, b: S_cusp * b });
  let L_cusp = Math.cbrt(1 / Math.max(rgb4.r, rgb4.g, rgb4.b));
  let C_cusp = L_cusp * S_cusp;
  return [L_cusp, C_cusp];
}
function find_gamut_intersection(a, b, L1, C12, L0, cusp = null) {
  if (!cusp) {
    cusp = find_cusp(a, b);
  }
  let t;
  if ((L1 - L0) * cusp[1] - (cusp[0] - L0) * C12 <= 0) {
    t = cusp[1] * L0 / (C12 * cusp[0] + cusp[1] * (L0 - L1));
  } else {
    t = cusp[1] * (L0 - 1) / (C12 * (cusp[0] - 1) + cusp[1] * (L0 - L1));
    {
      let dL = L1 - L0;
      let dC = C12;
      let k_l = 0.3963377774 * a + 0.2158037573 * b;
      let k_m = -0.1055613458 * a - 0.0638541728 * b;
      let k_s = -0.0894841775 * a - 1.291485548 * b;
      let l_dt = dL + dC * k_l;
      let m_dt = dL + dC * k_m;
      let s_dt = dL + dC * k_s;
      {
        let L = L0 * (1 - t) + t * L1;
        let C = t * C12;
        let l_ = L + C * k_l;
        let m_ = L + C * k_m;
        let s_ = L + C * k_s;
        let l = l_ * l_ * l_;
        let m = m_ * m_ * m_;
        let s = s_ * s_ * s_;
        let ldt = 3 * l_dt * l_ * l_;
        let mdt = 3 * m_dt * m_ * m_;
        let sdt = 3 * s_dt * s_ * s_;
        let ldt2 = 6 * l_dt * l_dt * l_;
        let mdt2 = 6 * m_dt * m_dt * m_;
        let sdt2 = 6 * s_dt * s_dt * s_;
        let r2 = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s - 1;
        let r1 = 4.0767416621 * ldt - 3.3077115913 * mdt + 0.2309699292 * sdt;
        let r22 = 4.0767416621 * ldt2 - 3.3077115913 * mdt2 + 0.2309699292 * sdt2;
        let u_r = r1 / (r1 * r1 - 0.5 * r2 * r22);
        let t_r = -r2 * u_r;
        let g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s - 1;
        let g1 = -1.2684380046 * ldt + 2.6097574011 * mdt - 0.3413193965 * sdt;
        let g2 = -1.2684380046 * ldt2 + 2.6097574011 * mdt2 - 0.3413193965 * sdt2;
        let u_g = g1 / (g1 * g1 - 0.5 * g * g2);
        let t_g = -g * u_g;
        let b2 = -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s - 1;
        let b1 = -0.0041960863 * ldt - 0.7034186147 * mdt + 1.707614701 * sdt;
        let b22 = -0.0041960863 * ldt2 - 0.7034186147 * mdt2 + 1.707614701 * sdt2;
        let u_b = b1 / (b1 * b1 - 0.5 * b2 * b22);
        let t_b = -b2 * u_b;
        t_r = u_r >= 0 ? t_r : 1e6;
        t_g = u_g >= 0 ? t_g : 1e6;
        t_b = u_b >= 0 ? t_b : 1e6;
        t += Math.min(t_r, Math.min(t_g, t_b));
      }
    }
  }
  return t;
}
function get_ST_max(a_, b_, cusp = null) {
  if (!cusp) {
    cusp = find_cusp(a_, b_);
  }
  let L = cusp[0];
  let C = cusp[1];
  return [C / L, C / (1 - L)];
}
function get_Cs(L, a_, b_) {
  let cusp = find_cusp(a_, b_);
  let C_max = find_gamut_intersection(a_, b_, L, 1, L, cusp);
  let ST_max = get_ST_max(a_, b_, cusp);
  let S_mid = 0.11516993 + 1 / (7.4477897 + 4.1590124 * b_ + a_ * (-2.19557347 + 1.75198401 * b_ + a_ * (-2.13704948 - 10.02301043 * b_ + a_ * (-4.24894561 + 5.38770819 * b_ + 4.69891013 * a_))));
  let T_mid = 0.11239642 + 1 / (1.6132032 - 0.68124379 * b_ + a_ * (0.40370612 + 0.90148123 * b_ + a_ * (-0.27087943 + 0.6122399 * b_ + a_ * (299215e-8 - 0.45399568 * b_ - 0.14661872 * a_))));
  let k4 = C_max / Math.min(L * ST_max[0], (1 - L) * ST_max[1]);
  let C_a = L * S_mid;
  let C_b = (1 - L) * T_mid;
  let C_mid = 0.9 * k4 * Math.sqrt(
    Math.sqrt(
      1 / (1 / (C_a * C_a * C_a * C_a) + 1 / (C_b * C_b * C_b * C_b))
    )
  );
  C_a = L * 0.4;
  C_b = (1 - L) * 0.8;
  let C_0 = Math.sqrt(1 / (1 / (C_a * C_a) + 1 / (C_b * C_b)));
  return [C_0, C_mid, C_max];
}

// node_modules/culori/src/okhsl/convertOklabToOkhsl.js
function convertOklabToOkhsl(lab2) {
  const l = lab2.l !== void 0 ? lab2.l : 0;
  const a = lab2.a !== void 0 ? lab2.a : 0;
  const b = lab2.b !== void 0 ? lab2.b : 0;
  const ret = { mode: "okhsl", l: toe(l) };
  if (lab2.alpha !== void 0) {
    ret.alpha = lab2.alpha;
  }
  let c2 = Math.sqrt(a * a + b * b);
  if (!c2) {
    ret.s = 0;
    return ret;
  }
  let [C_0, C_mid, C_max] = get_Cs(l, a / c2, b / c2);
  let s;
  if (c2 < C_mid) {
    let k_0 = 0;
    let k_1 = 0.8 * C_0;
    let k_2 = 1 - k_1 / C_mid;
    let t = (c2 - k_0) / (k_1 + k_2 * (c2 - k_0));
    s = t * 0.8;
  } else {
    let k_0 = C_mid;
    let k_1 = 0.2 * C_mid * C_mid * 1.25 * 1.25 / C_0;
    let k_2 = 1 - k_1 / (C_max - C_mid);
    let t = (c2 - k_0) / (k_1 + k_2 * (c2 - k_0));
    s = 0.8 + 0.2 * t;
  }
  if (s) {
    ret.s = s;
    ret.h = normalizeHue_default(Math.atan2(b, a) * 180 / Math.PI);
  }
  return ret;
}

// node_modules/culori/src/okhsl/convertOkhslToOklab.js
function convertOkhslToOklab(hsl3) {
  let h = hsl3.h !== void 0 ? hsl3.h : 0;
  let s = hsl3.s !== void 0 ? hsl3.s : 0;
  let l = hsl3.l !== void 0 ? hsl3.l : 0;
  const ret = { mode: "oklab", l: toe_inv(l) };
  if (hsl3.alpha !== void 0) {
    ret.alpha = hsl3.alpha;
  }
  if (!s || l === 1) {
    ret.a = ret.b = 0;
    return ret;
  }
  let a_ = Math.cos(h / 180 * Math.PI);
  let b_ = Math.sin(h / 180 * Math.PI);
  let [C_0, C_mid, C_max] = get_Cs(ret.l, a_, b_);
  let t, k_0, k_1, k_2;
  if (s < 0.8) {
    t = 1.25 * s;
    k_0 = 0;
    k_1 = 0.8 * C_0;
    k_2 = 1 - k_1 / C_mid;
  } else {
    t = 5 * (s - 0.8);
    k_0 = C_mid;
    k_1 = 0.2 * C_mid * C_mid * 1.25 * 1.25 / C_0;
    k_2 = 1 - k_1 / (C_max - C_mid);
  }
  let C = k_0 + t * k_1 / (1 - k_2 * t);
  ret.a = C * a_;
  ret.b = C * b_;
  return ret;
}

// node_modules/culori/src/okhsl/modeOkhsl.js
var modeOkhsl = {
  ...definition_default7,
  mode: "okhsl",
  channels: ["h", "s", "l", "alpha"],
  parse: ["--okhsl"],
  serialize: "--okhsl",
  fromMode: {
    oklab: convertOklabToOkhsl,
    rgb: (c2) => convertOklabToOkhsl(convertRgbToOklab_default(c2))
  },
  toMode: {
    oklab: convertOkhslToOklab,
    rgb: (c2) => convertOklabToRgb_default(convertOkhslToOklab(c2))
  }
};
var modeOkhsl_default = modeOkhsl;

// node_modules/culori/src/okhsv/convertOklabToOkhsv.js
function convertOklabToOkhsv(lab2) {
  let l = lab2.l !== void 0 ? lab2.l : 0;
  let a = lab2.a !== void 0 ? lab2.a : 0;
  let b = lab2.b !== void 0 ? lab2.b : 0;
  let c2 = Math.sqrt(a * a + b * b);
  let a_ = c2 ? a / c2 : 1;
  let b_ = c2 ? b / c2 : 1;
  let [S_max, T] = get_ST_max(a_, b_);
  let S_0 = 0.5;
  let k4 = 1 - S_0 / S_max;
  let t = T / (c2 + l * T);
  let L_v = t * l;
  let C_v = t * c2;
  let L_vt = toe_inv(L_v);
  let C_vt = C_v * L_vt / L_v;
  let rgb_scale = convertOklabToLrgb_default({ l: L_vt, a: a_ * C_vt, b: b_ * C_vt });
  let scale_L = Math.cbrt(
    1 / Math.max(rgb_scale.r, rgb_scale.g, rgb_scale.b, 0)
  );
  l = l / scale_L;
  c2 = c2 / scale_L * toe(l) / l;
  l = toe(l);
  const ret = {
    mode: "okhsv",
    s: c2 ? (S_0 + T) * C_v / (T * S_0 + T * k4 * C_v) : 0,
    v: l ? l / L_v : 0
  };
  if (ret.s) {
    ret.h = normalizeHue_default(Math.atan2(b, a) * 180 / Math.PI);
  }
  if (lab2.alpha !== void 0) {
    ret.alpha = lab2.alpha;
  }
  return ret;
}

// node_modules/culori/src/okhsv/convertOkhsvToOklab.js
function convertOkhsvToOklab(hsv2) {
  const ret = { mode: "oklab" };
  if (hsv2.alpha !== void 0) {
    ret.alpha = hsv2.alpha;
  }
  const h = hsv2.h !== void 0 ? hsv2.h : 0;
  const s = hsv2.s !== void 0 ? hsv2.s : 0;
  const v = hsv2.v !== void 0 ? hsv2.v : 0;
  const a_ = Math.cos(h / 180 * Math.PI);
  const b_ = Math.sin(h / 180 * Math.PI);
  const [S_max, T] = get_ST_max(a_, b_);
  const S_0 = 0.5;
  const k4 = 1 - S_0 / S_max;
  const L_v = 1 - s * S_0 / (S_0 + T - T * k4 * s);
  const C_v = s * T * S_0 / (S_0 + T - T * k4 * s);
  const L_vt = toe_inv(L_v);
  const C_vt = C_v * L_vt / L_v;
  const rgb_scale = convertOklabToLrgb_default({
    l: L_vt,
    a: a_ * C_vt,
    b: b_ * C_vt
  });
  const scale_L = Math.cbrt(
    1 / Math.max(rgb_scale.r, rgb_scale.g, rgb_scale.b, 0)
  );
  const L_new = toe_inv(v * L_v);
  const C = C_v * L_new / L_v;
  ret.l = L_new * scale_L;
  ret.a = C * a_ * scale_L;
  ret.b = C * b_ * scale_L;
  return ret;
}

// node_modules/culori/src/okhsv/modeOkhsv.js
var modeOkhsv = {
  ...definition_default8,
  mode: "okhsv",
  channels: ["h", "s", "v", "alpha"],
  parse: ["--okhsv"],
  serialize: "--okhsv",
  fromMode: {
    oklab: convertOklabToOkhsv,
    rgb: (c2) => convertOklabToOkhsv(convertRgbToOklab_default(c2))
  },
  toMode: {
    oklab: convertOkhsvToOklab,
    rgb: (c2) => convertOklabToRgb_default(convertOkhsvToOklab(c2))
  }
};
var modeOkhsv_default = modeOkhsv;

// node_modules/culori/src/oklab/parseOklab.js
function parseOklab(color, parsed) {
  if (!parsed || parsed[0] !== "oklab") {
    return void 0;
  }
  const res = { mode: "oklab" };
  const [, l, a, b, alpha] = parsed;
  if (l.type === Tok.Hue || a.type === Tok.Hue || b.type === Tok.Hue) {
    return void 0;
  }
  if (l.type !== Tok.None) {
    res.l = Math.min(
      Math.max(0, l.type === Tok.Number ? l.value : l.value / 100),
      1
    );
  }
  if (a.type !== Tok.None) {
    res.a = a.type === Tok.Number ? a.value : a.value * 0.4 / 100;
  }
  if (b.type !== Tok.None) {
    res.b = b.type === Tok.Number ? b.value : b.value * 0.4 / 100;
  }
  if (alpha.type !== Tok.None) {
    res.alpha = Math.min(
      1,
      Math.max(
        0,
        alpha.type === Tok.Number ? alpha.value : alpha.value / 100
      )
    );
  }
  return res;
}
var parseOklab_default = parseOklab;

// node_modules/culori/src/oklab/definition.js
var definition20 = {
  ...definition_default13,
  mode: "oklab",
  toMode: {
    lrgb: convertOklabToLrgb_default,
    rgb: convertOklabToRgb_default
  },
  fromMode: {
    lrgb: convertLrgbToOklab_default,
    rgb: convertRgbToOklab_default
  },
  ranges: {
    l: [0, 1],
    a: [-0.4, 0.4],
    b: [-0.4, 0.4]
  },
  parse: [parseOklab_default],
  serialize: (c2) => `oklab(${c2.l !== void 0 ? c2.l : "none"} ${c2.a !== void 0 ? c2.a : "none"} ${c2.b !== void 0 ? c2.b : "none"}${c2.alpha < 1 ? ` / ${c2.alpha}` : ""})`
};
var definition_default20 = definition20;

// node_modules/culori/src/oklch/parseOklch.js
function parseOklch(color, parsed) {
  if (!parsed || parsed[0] !== "oklch") {
    return void 0;
  }
  const res = { mode: "oklch" };
  const [, l, c2, h, alpha] = parsed;
  if (l.type !== Tok.None) {
    if (l.type === Tok.Hue) {
      return void 0;
    }
    res.l = Math.min(
      Math.max(0, l.type === Tok.Number ? l.value : l.value / 100),
      1
    );
  }
  if (c2.type !== Tok.None) {
    res.c = Math.max(
      0,
      c2.type === Tok.Number ? c2.value : c2.value * 0.4 / 100
    );
  }
  if (h.type !== Tok.None) {
    if (h.type === Tok.Percentage) {
      return void 0;
    }
    res.h = h.value;
  }
  if (alpha.type !== Tok.None) {
    res.alpha = Math.min(
      1,
      Math.max(
        0,
        alpha.type === Tok.Number ? alpha.value : alpha.value / 100
      )
    );
  }
  return res;
}
var parseOklch_default = parseOklch;

// node_modules/culori/src/oklch/definition.js
var definition21 = {
  ...definition_default15,
  mode: "oklch",
  toMode: {
    oklab: (c2) => convertLchToLab_default(c2, "oklab"),
    rgb: (c2) => convertOklabToRgb_default(convertLchToLab_default(c2, "oklab"))
  },
  fromMode: {
    rgb: (c2) => convertLabToLch_default(convertRgbToOklab_default(c2), "oklch"),
    oklab: (c2) => convertLabToLch_default(c2, "oklch")
  },
  parse: [parseOklch_default],
  serialize: (c2) => `oklch(${c2.l !== void 0 ? c2.l : "none"} ${c2.c !== void 0 ? c2.c : "none"} ${c2.h !== void 0 ? c2.h : "none"}${c2.alpha < 1 ? ` / ${c2.alpha}` : ""})`,
  ranges: {
    l: [0, 1],
    c: [0, 0.4],
    h: [0, 360]
  }
};
var definition_default21 = definition21;

// node_modules/culori/src/p3/convertP3ToXyz65.js
var convertP3ToXyz65 = (rgb4) => {
  let { r: r2, g, b, alpha } = convertRgbToLrgb_default(rgb4);
  let res = {
    mode: "xyz65",
    x: 0.486570948648216 * r2 + 0.265667693169093 * g + 0.1982172852343625 * b,
    y: 0.2289745640697487 * r2 + 0.6917385218365062 * g + 0.079286914093745 * b,
    z: 0 * r2 + 0.0451133818589026 * g + 1.043944368900976 * b
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertP3ToXyz65_default = convertP3ToXyz65;

// node_modules/culori/src/p3/convertXyz65ToP3.js
var convertXyz65ToP3 = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let res = convertLrgbToRgb_default(
    {
      r: x * 2.4934969119414263 - y * 0.9313836179191242 - 0.402710784450717 * z,
      g: x * -0.8294889695615749 + y * 1.7626640603183465 + 0.0236246858419436 * z,
      b: x * 0.0358458302437845 - y * 0.0761723892680418 + 0.9568845240076871 * z
    },
    "p3"
  );
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz65ToP3_default = convertXyz65ToP3;

// node_modules/culori/src/p3/definition.js
var definition22 = {
  ...definition_default,
  mode: "p3",
  parse: ["display-p3"],
  serialize: "display-p3",
  fromMode: {
    rgb: (color) => convertXyz65ToP3_default(convertRgbToXyz65_default(color)),
    xyz65: convertXyz65ToP3_default
  },
  toMode: {
    rgb: (color) => convertXyz65ToRgb_default(convertP3ToXyz65_default(color)),
    xyz65: convertP3ToXyz65_default
  }
};
var definition_default22 = definition22;

// node_modules/culori/src/prophoto/convertXyz50ToProphoto.js
var gamma2 = (v) => {
  let abs2 = Math.abs(v);
  if (abs2 >= 1 / 512) {
    return Math.sign(v) * Math.pow(abs2, 1 / 1.8);
  }
  return 16 * v;
};
var convertXyz50ToProphoto = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let res = {
    mode: "prophoto",
    r: gamma2(
      x * 1.3457868816471585 - y * 0.2555720873797946 - 0.0511018649755453 * z
    ),
    g: gamma2(
      x * -0.5446307051249019 + y * 1.5082477428451466 + 0.0205274474364214 * z
    ),
    b: gamma2(x * 0 + y * 0 + 1.2119675456389452 * z)
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz50ToProphoto_default = convertXyz50ToProphoto;

// node_modules/culori/src/prophoto/convertProphotoToXyz50.js
var linearize2 = (v = 0) => {
  let abs2 = Math.abs(v);
  if (abs2 >= 16 / 512) {
    return Math.sign(v) * Math.pow(abs2, 1.8);
  }
  return v / 16;
};
var convertProphotoToXyz50 = (prophoto2) => {
  let r2 = linearize2(prophoto2.r);
  let g = linearize2(prophoto2.g);
  let b = linearize2(prophoto2.b);
  let res = {
    mode: "xyz50",
    x: 0.7977666449006423 * r2 + 0.1351812974005331 * g + 0.0313477341283922 * b,
    y: 0.2880748288194013 * r2 + 0.7118352342418731 * g + 899369387256e-16 * b,
    z: 0 * r2 + 0 * g + 0.8251046025104602 * b
  };
  if (prophoto2.alpha !== void 0) {
    res.alpha = prophoto2.alpha;
  }
  return res;
};
var convertProphotoToXyz50_default = convertProphotoToXyz50;

// node_modules/culori/src/prophoto/definition.js
var definition23 = {
  ...definition_default,
  mode: "prophoto",
  parse: ["prophoto-rgb"],
  serialize: "prophoto-rgb",
  fromMode: {
    xyz50: convertXyz50ToProphoto_default,
    rgb: (color) => convertXyz50ToProphoto_default(convertRgbToXyz50_default(color))
  },
  toMode: {
    xyz50: convertProphotoToXyz50_default,
    rgb: (color) => convertXyz50ToRgb_default(convertProphotoToXyz50_default(color))
  }
};
var definition_default23 = definition23;

// node_modules/culori/src/rec2020/convertXyz65ToRec2020.js
var \u03B1 = 1.09929682680944;
var \u03B2 = 0.018053968510807;
var gamma3 = (v) => {
  const abs2 = Math.abs(v);
  if (abs2 > \u03B2) {
    return (Math.sign(v) || 1) * (\u03B1 * Math.pow(abs2, 0.45) - (\u03B1 - 1));
  }
  return 4.5 * v;
};
var convertXyz65ToRec2020 = ({ x, y, z, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let res = {
    mode: "rec2020",
    r: gamma3(
      x * 1.7166511879712683 - y * 0.3556707837763925 - 0.2533662813736599 * z
    ),
    g: gamma3(
      x * -0.6666843518324893 + y * 1.6164812366349395 + 0.0157685458139111 * z
    ),
    b: gamma3(
      x * 0.0176398574453108 - y * 0.0427706132578085 + 0.9421031212354739 * z
    )
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz65ToRec2020_default = convertXyz65ToRec2020;

// node_modules/culori/src/rec2020/convertRec2020ToXyz65.js
var \u03B12 = 1.09929682680944;
var \u03B22 = 0.018053968510807;
var linearize3 = (v = 0) => {
  let abs2 = Math.abs(v);
  if (abs2 < \u03B22 * 4.5) {
    return v / 4.5;
  }
  return (Math.sign(v) || 1) * Math.pow((abs2 + \u03B12 - 1) / \u03B12, 1 / 0.45);
};
var convertRec2020ToXyz65 = (rec20202) => {
  let r2 = linearize3(rec20202.r);
  let g = linearize3(rec20202.g);
  let b = linearize3(rec20202.b);
  let res = {
    mode: "xyz65",
    x: 0.6369580483012911 * r2 + 0.1446169035862083 * g + 0.1688809751641721 * b,
    y: 0.262700212011267 * r2 + 0.6779980715188708 * g + 0.059301716469862 * b,
    z: 0 * r2 + 0.0280726930490874 * g + 1.0609850577107909 * b
  };
  if (rec20202.alpha !== void 0) {
    res.alpha = rec20202.alpha;
  }
  return res;
};
var convertRec2020ToXyz65_default = convertRec2020ToXyz65;

// node_modules/culori/src/rec2020/definition.js
var definition24 = {
  ...definition_default,
  mode: "rec2020",
  fromMode: {
    xyz65: convertXyz65ToRec2020_default,
    rgb: (color) => convertXyz65ToRec2020_default(convertRgbToXyz65_default(color))
  },
  toMode: {
    xyz65: convertRec2020ToXyz65_default,
    rgb: (color) => convertXyz65ToRgb_default(convertRec2020ToXyz65_default(color))
  },
  parse: ["rec2020"],
  serialize: "rec2020"
};
var definition_default24 = definition24;

// node_modules/culori/src/xyb/constants.js
var bias = 0.0037930732552754493;
var bias_cbrt = Math.cbrt(bias);

// node_modules/culori/src/xyb/convertRgbToXyb.js
var transfer = (v) => Math.cbrt(v) - bias_cbrt;
var convertRgbToXyb = (color) => {
  const { r: r2, g, b, alpha } = convertRgbToLrgb_default(color);
  const l = transfer(0.3 * r2 + 0.622 * g + 0.078 * b + bias);
  const m = transfer(0.23 * r2 + 0.692 * g + 0.078 * b + bias);
  const s = transfer(
    0.2434226892454782 * r2 + 0.2047674442449682 * g + 0.5518098665095535 * b + bias
  );
  const res = {
    mode: "xyb",
    x: (l - m) / 2,
    y: (l + m) / 2,
    /* Apply default chroma from luma (subtract Y from B) */
    b: s - (l + m) / 2
  };
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertRgbToXyb_default = convertRgbToXyb;

// node_modules/culori/src/xyb/convertXybToRgb.js
var transfer2 = (v) => Math.pow(v + bias_cbrt, 3);
var convertXybToRgb = ({ x, y, b, alpha }) => {
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (b === void 0) b = 0;
  const l = transfer2(x + y) - bias;
  const m = transfer2(y - x) - bias;
  const s = transfer2(b + y) - bias;
  const res = convertLrgbToRgb_default({
    r: 11.031566904639861 * l - 9.866943908131562 * m - 0.16462299650829934 * s,
    g: -3.2541473810744237 * l + 4.418770377582723 * m - 0.16462299650829934 * s,
    b: -3.6588512867136815 * l + 2.7129230459360922 * m + 1.9459282407775895 * s
  });
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertXybToRgb_default = convertXybToRgb;

// node_modules/culori/src/xyb/definition.js
var definition25 = {
  mode: "xyb",
  channels: ["x", "y", "b", "alpha"],
  parse: ["--xyb"],
  serialize: "--xyb",
  toMode: {
    rgb: convertXybToRgb_default
  },
  fromMode: {
    rgb: convertRgbToXyb_default
  },
  ranges: {
    x: [-0.0154, 0.0281],
    y: [0, 0.8453],
    b: [-0.2778, 0.388]
  },
  interpolate: {
    x: interpolatorLinear,
    y: interpolatorLinear,
    b: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  }
};
var definition_default25 = definition25;

// node_modules/culori/src/xyz50/definition.js
var definition26 = {
  mode: "xyz50",
  parse: ["xyz-d50"],
  serialize: "xyz-d50",
  toMode: {
    rgb: convertXyz50ToRgb_default,
    lab: convertXyz50ToLab_default
  },
  fromMode: {
    rgb: convertRgbToXyz50_default,
    lab: convertLabToXyz50_default
  },
  channels: ["x", "y", "z", "alpha"],
  ranges: {
    x: [0, 0.964],
    y: [0, 0.999],
    z: [0, 0.825]
  },
  interpolate: {
    x: interpolatorLinear,
    y: interpolatorLinear,
    z: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  }
};
var definition_default26 = definition26;

// node_modules/culori/src/xyz65/convertXyz65ToXyz50.js
var convertXyz65ToXyz50 = (xyz652) => {
  let { x, y, z, alpha } = xyz652;
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let res = {
    mode: "xyz50",
    x: 1.0479298208405488 * x + 0.0229467933410191 * y - 0.0501922295431356 * z,
    y: 0.0296278156881593 * x + 0.990434484573249 * y - 0.0170738250293851 * z,
    z: -0.0092430581525912 * x + 0.0150551448965779 * y + 0.7518742899580008 * z
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz65ToXyz50_default = convertXyz65ToXyz50;

// node_modules/culori/src/xyz65/convertXyz50ToXyz65.js
var convertXyz50ToXyz65 = (xyz502) => {
  let { x, y, z, alpha } = xyz502;
  if (x === void 0) x = 0;
  if (y === void 0) y = 0;
  if (z === void 0) z = 0;
  let res = {
    mode: "xyz65",
    x: 0.9554734527042182 * x - 0.0230985368742614 * y + 0.0632593086610217 * z,
    y: -0.0283697069632081 * x + 1.0099954580058226 * y + 0.021041398966943 * z,
    z: 0.0123140016883199 * x - 0.0205076964334779 * y + 1.3303659366080753 * z
  };
  if (alpha !== void 0) {
    res.alpha = alpha;
  }
  return res;
};
var convertXyz50ToXyz65_default = convertXyz50ToXyz65;

// node_modules/culori/src/xyz65/definition.js
var definition27 = {
  mode: "xyz65",
  toMode: {
    rgb: convertXyz65ToRgb_default,
    xyz50: convertXyz65ToXyz50_default
  },
  fromMode: {
    rgb: convertRgbToXyz65_default,
    xyz50: convertXyz50ToXyz65_default
  },
  ranges: {
    x: [0, 0.95],
    y: [0, 1],
    z: [0, 1.088]
  },
  channels: ["x", "y", "z", "alpha"],
  parse: ["xyz", "xyz-d65"],
  serialize: "xyz-d65",
  interpolate: {
    x: interpolatorLinear,
    y: interpolatorLinear,
    z: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  }
};
var definition_default27 = definition27;

// node_modules/culori/src/yiq/convertRgbToYiq.js
var convertRgbToYiq = ({ r: r2, g, b, alpha }) => {
  if (r2 === void 0) r2 = 0;
  if (g === void 0) g = 0;
  if (b === void 0) b = 0;
  const res = {
    mode: "yiq",
    y: 0.29889531 * r2 + 0.58662247 * g + 0.11448223 * b,
    i: 0.59597799 * r2 - 0.2741761 * g - 0.32180189 * b,
    q: 0.21147017 * r2 - 0.52261711 * g + 0.31114694 * b
  };
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertRgbToYiq_default = convertRgbToYiq;

// node_modules/culori/src/yiq/convertYiqToRgb.js
var convertYiqToRgb = ({ y, i, q, alpha }) => {
  if (y === void 0) y = 0;
  if (i === void 0) i = 0;
  if (q === void 0) q = 0;
  const res = {
    mode: "rgb",
    r: y + 0.95608445 * i + 0.6208885 * q,
    g: y - 0.27137664 * i - 0.6486059 * q,
    b: y - 1.10561724 * i + 1.70250126 * q
  };
  if (alpha !== void 0) res.alpha = alpha;
  return res;
};
var convertYiqToRgb_default = convertYiqToRgb;

// node_modules/culori/src/yiq/definition.js
var definition28 = {
  mode: "yiq",
  toMode: {
    rgb: convertYiqToRgb_default
  },
  fromMode: {
    rgb: convertRgbToYiq_default
  },
  channels: ["y", "i", "q", "alpha"],
  parse: ["--yiq"],
  serialize: "--yiq",
  ranges: {
    i: [-0.595, 0.595],
    q: [-0.522, 0.522]
  },
  interpolate: {
    y: interpolatorLinear,
    i: interpolatorLinear,
    q: interpolatorLinear,
    alpha: { use: interpolatorLinear, fixup: fixupAlpha }
  }
};
var definition_default28 = definition28;

// node_modules/culori/src/round.js
var r = (value, precision) => Math.round(value * (precision = Math.pow(10, precision))) / precision;
var round = (precision = 4) => (value) => typeof value === "number" ? r(value, precision) : value;
var round_default = round;

// node_modules/culori/src/formatter.js
var twoDecimals = round_default(2);
var clamp = (value) => Math.max(0, Math.min(1, value || 0));
var fixup = (value) => Math.round(clamp(value) * 255);
var rgb = converter_default("rgb");
var hsl = converter_default("hsl");
var serializeHex = (color) => {
  if (color === void 0) {
    return void 0;
  }
  let r2 = fixup(color.r);
  let g = fixup(color.g);
  let b = fixup(color.b);
  return "#" + (1 << 24 | r2 << 16 | g << 8 | b).toString(16).slice(1);
};
var formatHex = (c2) => serializeHex(rgb(c2));

// node_modules/culori/src/deficiency.js
var rgb2 = converter_default("rgb");
var PROT = [
  [1, 0, -0, 0, 1, 0, -0, -0, 1],
  [
    0.856167,
    0.182038,
    -0.038205,
    0.029342,
    0.955115,
    0.015544,
    -288e-5,
    -1563e-6,
    1.004443
  ],
  [
    0.734766,
    0.334872,
    -0.069637,
    0.05184,
    0.919198,
    0.028963,
    -4928e-6,
    -4209e-6,
    1.009137
  ],
  [
    0.630323,
    0.465641,
    -0.095964,
    0.069181,
    0.890046,
    0.040773,
    -6308e-6,
    -7724e-6,
    1.014032
  ],
  [
    0.539009,
    0.579343,
    -0.118352,
    0.082546,
    0.866121,
    0.051332,
    -7136e-6,
    -0.011959,
    1.019095
  ],
  [
    0.458064,
    0.679578,
    -0.137642,
    0.092785,
    0.846313,
    0.060902,
    -7494e-6,
    -0.016807,
    1.024301
  ],
  [
    0.38545,
    0.769005,
    -0.154455,
    0.100526,
    0.829802,
    0.069673,
    -7442e-6,
    -0.02219,
    1.029632
  ],
  [
    0.319627,
    0.849633,
    -0.169261,
    0.106241,
    0.815969,
    0.07779,
    -7025e-6,
    -0.028051,
    1.035076
  ],
  [
    0.259411,
    0.923008,
    -0.18242,
    0.110296,
    0.80434,
    0.085364,
    -6276e-6,
    -0.034346,
    1.040622
  ],
  [
    0.203876,
    0.990338,
    -0.194214,
    0.112975,
    0.794542,
    0.092483,
    -5222e-6,
    -0.041043,
    1.046265
  ],
  [
    0.152286,
    1.052583,
    -0.204868,
    0.114503,
    0.786281,
    0.099216,
    -3882e-6,
    -0.048116,
    1.051998
  ]
];
var DEUTER = [
  [1, 0, -0, 0, 1, 0, -0, -0, 1],
  [
    0.866435,
    0.177704,
    -0.044139,
    0.049567,
    0.939063,
    0.01137,
    -3453e-6,
    7233e-6,
    0.99622
  ],
  [
    0.760729,
    0.319078,
    -0.079807,
    0.090568,
    0.889315,
    0.020117,
    -6027e-6,
    0.013325,
    0.992702
  ],
  [
    0.675425,
    0.43385,
    -0.109275,
    0.125303,
    0.847755,
    0.026942,
    -795e-5,
    0.018572,
    0.989378
  ],
  [
    0.605511,
    0.52856,
    -0.134071,
    0.155318,
    0.812366,
    0.032316,
    -9376e-6,
    0.023176,
    0.9862
  ],
  [
    0.547494,
    0.607765,
    -0.155259,
    0.181692,
    0.781742,
    0.036566,
    -0.01041,
    0.027275,
    0.983136
  ],
  [
    0.498864,
    0.674741,
    -0.173604,
    0.205199,
    0.754872,
    0.039929,
    -0.011131,
    0.030969,
    0.980162
  ],
  [
    0.457771,
    0.731899,
    -0.18967,
    0.226409,
    0.731012,
    0.042579,
    -0.011595,
    0.034333,
    0.977261
  ],
  [
    0.422823,
    0.781057,
    -0.203881,
    0.245752,
    0.709602,
    0.044646,
    -0.011843,
    0.037423,
    0.974421
  ],
  [
    0.392952,
    0.82361,
    -0.216562,
    0.263559,
    0.69021,
    0.046232,
    -0.01191,
    0.040281,
    0.97163
  ],
  [
    0.367322,
    0.860646,
    -0.227968,
    0.280085,
    0.672501,
    0.047413,
    -0.01182,
    0.04294,
    0.968881
  ]
];
var TRIT = [
  [1, 0, -0, 0, 1, 0, -0, -0, 1],
  [
    0.92667,
    0.092514,
    -0.019184,
    0.021191,
    0.964503,
    0.014306,
    8437e-6,
    0.054813,
    0.93675
  ],
  [
    0.89572,
    0.13333,
    -0.02905,
    0.029997,
    0.9454,
    0.024603,
    0.013027,
    0.104707,
    0.882266
  ],
  [
    0.905871,
    0.127791,
    -0.033662,
    0.026856,
    0.941251,
    0.031893,
    0.01341,
    0.148296,
    0.838294
  ],
  [
    0.948035,
    0.08949,
    -0.037526,
    0.014364,
    0.946792,
    0.038844,
    0.010853,
    0.193991,
    0.795156
  ],
  [
    1.017277,
    0.027029,
    -0.044306,
    -6113e-6,
    0.958479,
    0.047634,
    6379e-6,
    0.248708,
    0.744913
  ],
  [
    1.104996,
    -0.046633,
    -0.058363,
    -0.032137,
    0.971635,
    0.060503,
    1336e-6,
    0.317922,
    0.680742
  ],
  [
    1.193214,
    -0.109812,
    -0.083402,
    -0.058496,
    0.97941,
    0.079086,
    -2346e-6,
    0.403492,
    0.598854
  ],
  [
    1.257728,
    -0.139648,
    -0.118081,
    -0.078003,
    0.975409,
    0.102594,
    -3316e-6,
    0.501214,
    0.502102
  ],
  [
    1.278864,
    -0.125333,
    -0.153531,
    -0.084748,
    0.957674,
    0.127074,
    -989e-6,
    0.601151,
    0.399838
  ],
  [
    1.255528,
    -0.076749,
    -0.178779,
    -0.078411,
    0.930809,
    0.147602,
    4733e-6,
    0.691367,
    0.3039
  ]
];
var deficiency = (lut, t) => {
  let tt = Math.max(0, Math.min(1, t));
  let i = Math.round(tt / 0.1);
  let w = Math.round(tt % 0.1);
  let arr = lut[i];
  if (w > 0 && i < lut.length - 1) {
    let arr_2 = lut[i + 1];
    arr = arr.map((v, idx) => lerp2(arr[idx], arr_2[idx], w));
  }
  return (color) => {
    let c2 = prepare_default(color);
    if (c2 === void 0) {
      return void 0;
    }
    let { r: r2, g, b } = rgb2(c2);
    let ret = {
      mode: "rgb",
      r: arr[0] * r2 + arr[1] * g + arr[2] * b,
      g: arr[3] * r2 + arr[4] * g + arr[5] * b,
      b: arr[6] * r2 + arr[7] * g + arr[8] * b
    };
    if (c2.alpha !== void 0) {
      ret.alpha = c2.alpha;
    }
    return converter_default(c2.mode)(ret);
  };
};
var filterDeficiencyProt = (severity = 1) => deficiency(PROT, severity);
var filterDeficiencyDeuter = (severity = 1) => deficiency(DEUTER, severity);
var filterDeficiencyTrit = (severity = 1) => deficiency(TRIT, severity);

// node_modules/culori/src/index.js
var a98 = useMode(definition_default2);
var cubehelix = useMode(definition_default3);
var dlab = useMode(definition_default4);
var dlch = useMode(definition_default5);
var hsi = useMode(definition_default6);
var hsl2 = useMode(definition_default7);
var hsv = useMode(definition_default8);
var hwb = useMode(definition_default9);
var itp = useMode(definition_default10);
var jab = useMode(definition_default11);
var jch = useMode(definition_default12);
var lab = useMode(definition_default13);
var lab65 = useMode(definition_default14);
var lch = useMode(definition_default15);
var lch65 = useMode(definition_default16);
var lchuv = useMode(definition_default17);
var lrgb = useMode(definition_default18);
var luv = useMode(definition_default19);
var okhsl = useMode(modeOkhsl_default);
var okhsv = useMode(modeOkhsv_default);
var oklab = useMode(definition_default20);
var oklch = useMode(definition_default21);
var p3 = useMode(definition_default22);
var prophoto = useMode(definition_default23);
var rec2020 = useMode(definition_default24);
var rgb3 = useMode(definition_default);
var xyb = useMode(definition_default25);
var xyz50 = useMode(definition_default26);
var xyz65 = useMode(definition_default27);
var yiq = useMode(definition_default28);
export {
  Blend,
  Hct,
  MaterialDynamicColors,
  SchemeFidelity,
  SchemeMonochrome,
  SchemeNeutral,
  SchemeTonalSpot,
  TonalPalette,
  argbFromHex,
  converter_default as converter,
  differenceEuclidean,
  filterDeficiencyDeuter,
  filterDeficiencyProt,
  filterDeficiencyTrit,
  formatHex,
  hexFromArgb,
  parse_default as parse
};
