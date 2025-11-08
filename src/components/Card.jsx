export default function Card({ title, subtitle, children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-white/20 bg-panel backdrop-blur-md p-6 shadow-md ${className}`}>
      {(title || subtitle) && (
        <div className="mb-4">
          {title && <h3 className="text-lg font-semibold text-white">{title}</h3>}
          {subtitle && <p className="text-sm text-white/80">{subtitle}</p>}
        </div>
      )}
      <div>{children}</div>
    </div>
  )
}
