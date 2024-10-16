/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './core/templates/core/authform.html',
    './core/templates/core/base.html',
    './core/templates/core/index.html',
    './core/templates/core/login.html',
    './core/templates/core/post.html',
    './core/templates/core/signup.html',
    './core/templates/core/welcome.html',
    './posts/templates/posts/explore.html',
    './posts/templates/posts/new.html',
    './posts/templates/posts/post_detail.html',
    './posts/templates/posts/saved.html',
    './users/templates/users/edit_profile.html',
    './users/templates/users/follow_stat.html',
    './users/templates/users/profile.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

