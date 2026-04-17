import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      keyframes: {
        capeFly: {
          '0%': { transform: 'rotate(-5deg)' },
          '100%': { transform: 'rotate(5deg)' },
        },
        pageTransition: {
          '0%': { transform: 'translateX(-300px)' },
          '45%': { transform: 'translateX(calc(50vw - 90px))' },
          '55%': { transform: 'translateX(calc(50vw - 90px))' },
          '100%': { transform: 'translateX(110vw)' },
        },
        rainFall: {
          '0%': { transform: 'translateY(-100px)' },
          '100%': { transform: 'translateY(110vh)' },
        },
        thunderFlash: {
          '0%, 100%': { opacity: '0' },
          '3%': { opacity: '0.4' },
          '6%': { opacity: '0' },
          '9%': { opacity: '0.6' },
          '12%': { opacity: '0' },
        },
        boltFlash: {
          '0%, 100%': { opacity: '0' },
          '20%': { opacity: '1' },
          '40%': { opacity: '0' },
          '60%': { opacity: '1' },
          '80%': { opacity: '0' },
        },
        slowRide: {
          '0%': { transform: 'translateX(-300px)' },
          '100%': { transform: 'translateX(120vw)' },
        },
        wave1: {
          '0%, 100%': { transform: 'translateX(0)' },
          '50%': { transform: 'translateX(-60px)' },
        },
        wave2: {
          '0%, 100%': { transform: 'translateX(-20px)' },
          '50%': { transform: 'translateX(40px)' },
        },
        wave3: {
          '0%, 100%': { transform: 'translateX(10px)' },
          '50%': { transform: 'translateX(-50px)' },
        },
        wheelSpin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        walk: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-8px)' },
        },
        ripple: {
          '0%': { transform: 'scale(0)', opacity: '1' },
          '100%': { transform: 'scale(1.5)', opacity: '0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
      animation: {
        capeFly: 'capeFly 0.4s ease-in-out infinite alternate',
        pageTransition: 'pageTransition 2.5s ease-in-out',
        rainFall: 'rainFall 0.8s linear infinite',
        thunderFlash: 'thunderFlash 8s infinite',
        boltFlash: 'boltFlash 0.6s infinite',
        slowRide: 'slowRide 18s linear infinite',
        wave1: 'wave1 5s infinite ease-in-out',
        wave2: 'wave2 7s infinite ease-in-out',
        wave3: 'wave3 9s infinite ease-in-out',
        wheelSpin: 'wheelSpin 0.5s linear infinite',
        walk: 'walk 0.6s ease-in-out infinite alternate',
        ripple: 'ripple 1.5s ease-out infinite',
        float: 'float 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
export default config;
