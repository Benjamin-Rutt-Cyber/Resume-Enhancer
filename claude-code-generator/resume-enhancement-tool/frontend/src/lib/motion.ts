import { Variants } from 'framer-motion';

/**
 * RE-VSION MOTION SYSTEM
 * 
 * Easing: Custom Quintic ease-out [0.23, 1, 0.32, 1]
 * Philosophy: Subtle, bottom-up entries, and high-quality deceleration.
 */

const SIGNATURE_EASE = [0.23, 1, 0.32, 1];
const STANDARD_DURATION = 0.4;
const FAST_DURATION = 0.2;

/**
 * 1. Page or Section Entry
 * A calm, vertical settle-in.
 */
export const fadeIn: Variants = {
    initial: {
        opacity: 0,
        y: 12
    },
    animate: {
        opacity: 1,
        y: 0,
        transition: {
            duration: STANDARD_DURATION,
            ease: SIGNATURE_EASE
        }
    },
    exit: {
        opacity: 0,
        y: -8,
        transition: {
            duration: FAST_DURATION,
            ease: [0.4, 0, 1, 1]
        }
    }
};

/**
 * 2. Staggered Children (Container)
 * Orchestrates a series of entries.
 */
export const staggerContainer: Variants = {
    initial: {},
    animate: {
        transition: {
            staggerChildren: 0.05,
            delayChildren: 0.1
        }
    }
};

/**
 * 3. Button or Card Hover
 * Subtle depth and focus. No bouncy scale.
 */
export const hoverScale: Variants = {
    initial: {
        scale: 1
    },
    hover: {
        scale: 1.02,
        transition: {
            duration: FAST_DURATION,
            ease: SIGNATURE_EASE
        }
    },
    tap: {
        scale: 0.98
    }
};

/**
 * 4. Loading / Processing State
 * A calm pulse for AI "thinking" moments.
 */
export const pulse: Variants = {
    animate: {
        opacity: [0.4, 0.7, 0.4],
        transition: {
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut"
        }
    }
};

/**
 * 5. Success or Reveal Moment
 * A slightly more pronounced entry for reassuring results.
 */
export const reveal: Variants = {
    initial: {
        opacity: 0,
        scale: 0.96
    },
    animate: {
        opacity: 1,
        scale: 1,
        transition: {
            duration: 0.5,
            ease: SIGNATURE_EASE
        }
    }
};

/**
 * 6. Modal / Overlay Entry
 * Centered entry with a slight scale up.
 */
export const modalVariant: Variants = {
    initial: {
        opacity: 0,
        scale: 0.98,
        y: 10
    },
    animate: {
        opacity: 1,
        scale: 1,
        y: 0,
        transition: {
            duration: STANDARD_DURATION,
            ease: SIGNATURE_EASE
        }
    },
    exit: {
        opacity: 0,
        scale: 0.98,
        transition: {
            duration: FAST_DURATION
        }
    }
};
