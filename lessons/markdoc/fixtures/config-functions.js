// A custom function callable from source as {% uppercase($title) %}.
// `parameters` arrives as an array of already-resolved values, positional
// arguments in call order, functions just take values in and return a
// value out, they don't touch the render tree directly.
export const uppercase = {
  transform(parameters) {
    return String(parameters[0]).toUpperCase();
  },
};
