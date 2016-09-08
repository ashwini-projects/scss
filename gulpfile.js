let gulp = require('gulp');
let sass = require('gulp-sass');

gulp.task('sass', () => {
  return gulp.src("style/scss/**/*.scss")
  .pipe(sass().on('error', sass.logError))
  .pipe(gulp.dest('style/'))
});

gulp.task('sass:watch', () => {
  gulp.watch("style/scss/**/*.scss", ['sass']);
  gulp.watch("*.js", ['sass']);
});

gulp.task('default', ['sass:watch', 'sass']);

