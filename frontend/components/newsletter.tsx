"use client"

import { Button } from "./ui/button"
import { motion } from "framer-motion"
import Link from "next/link"

export const Newsletter = () => {
  return (
    <div className="flex overflow-hidden relative flex-col gap-6 justify-center items-center pt-10 w-full h-full short:lg:pt-10 pb-footer-safe-area 2xl:pt-footer-safe-area px-sides short:lg:gap-6 lg:gap-8">
      <motion.div layout="position" transition={{ duration: 0.3, ease: "easeOut" }}>
        <h1 className="font-serif text-6xl sm:text-8xl lg:text-[12rem] text-white text-center drop-shadow-lg">
          ReefShield
        </h1>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, ease: "easeOut", delay: 0.3 }}
        className="max-w-5xl"
      >
        <p className="font-serif text-base sm:text-lg lg:text-2xl !leading-[1.6] font-medium text-center text-gray-100 drop-shadow-sm">
          ReefShield is an AI-powered alert system that monitors coral reefs with live satellite data, predicting
          bleaching risks, oil spills, and other threats to protect marine life and coastal communities.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: "easeOut", delay: 0.6 }}
        className="mt-8"
      >
        <Link href="/dashboard">
  <Button
    className="px-8 py-3 text-lg font-semibold text-white border border-white/20 shadow-xl backdrop-blur-md bg-white/10 hover:bg-white/20 hover:backdrop-blur-none transition-all duration-300 hover:shadow-2xl"
    size="lg"
  >
    View Dashboard
  </Button>
</Link>
      </motion.div>
    </div>
  )
}
