import Card from '../components/Card.jsx'
import CameraFeed from '../components/CameraFeed.jsx'
import { useSettings } from '../store/useStore'

export default function LiveFeed() {
  const { streamUrl } = useSettings()
  return (
    <div className="grid gap-6">
      <Card title="Live Feed" subtitle="ESP32-CAM stream">
        <CameraFeed streamUrl={streamUrl} />
      </Card>
    </div>
  )
}
