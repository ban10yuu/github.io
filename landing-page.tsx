import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Calendar } from "@/components/ui/calendar"
import { AirVent, WashingMachine, Utensils, Bath } from "lucide-react"
import Link from "next/link"
import { useState } from "react"

export default function LandingPage() {
  const [date, setDate] = useState<Date | undefined>(new Date())

  // 仮の空き日程データ
  const busyDates = [
    new Date(2024, 3, 10),
    new Date(2024, 3, 15),
    new Date(2024, 3, 20),
  ]

  return (
    <div className="flex flex-col min-h-screen bg-blue-50">
      <header className="px-4 lg:px-6 h-14 flex items-center bg-blue-600 text-white">
        <Link className="flex items-center justify-center" href="#">
          <span className="sr-only">ハタハタ</span>
          <span className="h-6 w-6 text-2xl">🐟</span>
          <span className="ml-2 text-2xl font-bold">ハタハタ</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#services">
            サービス
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#calendar">
            予約状況
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#testimonials">
            お客様の声
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#contact">
            お問い合わせ
          </Link>
        </nav>
      </header>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-blue-100">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none text-blue-800">
                  プロのクリーニングで、快適な生活を
                </h1>
                <p className="mx-auto max-w-[700px] text-blue-600 md:text-xl">
                  ハタハタは、あなたの家をより清潔で快適な空間にするお手伝いをします。
                </p>
              </div>
              <div className="space-x-4">
                <Button className="bg-blue-600 hover:bg-blue-700">サービスを見る</Button>
                <Button variant="outline" className="text-blue-600 border-blue-600 hover:bg-blue-100">お問い合わせ</Button>
              </div>
            </div>
          </div>
        </section>
        <section id="services" className="w-full py-12 md:py-24 lg:py-32 bg-white">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-12 text-blue-800">
              私たちのサービス
            </h2>
            <div className="flex justify-center space-x-8 mb-8">
              <Link href="/service/aircon" className="flex flex-col items-center text-center">
                <AirVent className="h-12 w-12 mb-4 text-blue-600" />
                <h3 className="text-xl font-bold mb-2 text-blue-800">エアコン<br />クリーニング</h3>
              </Link>
              <Link href="/service/washing-machine" className="flex flex-col items-center text-center">
                <WashingMachine className="h-12 w-12 mb-4 text-blue-600" />
                <h3 className="text-xl font-bold mb-2 text-blue-800">洗濯機<br />クリーニング</h3>
              </Link>
              <Link href="/service/range-hood" className="flex flex-col items-center text-center">
                <Utensils className="h-12 w-12 mb-4 text-blue-600" />
                <h3 className="text-xl font-bold mb-2 text-blue-800">レンジフード<br />クリーニング</h3>
              </Link>
              <Link href="/service/bath" className="flex flex-col items-center text-center">
                <Bath className="h-12 w-12 mb-4 text-blue-600" />
                <h3 className="text-xl font-bold mb-2 text-blue-800">風呂<br />クリーニング</h3>
              </Link>
            </div>
          </div>
        </section>
        <section id="calendar" className="w-full py-12 md:py-24 lg:py-32 bg-blue-50">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-12 text-blue-800">
              予約状況
            </h2>
            <div className="flex justify-center">
              <Calendar
                mode="single"
                selected={date}
                onSelect={setDate}
                className="rounded-md border shadow"
                disabled={(date) => busyDates.some(busyDate => 
                  busyDate.getDate() === date.getDate() &&
                  busyDate.getMonth() === date.getMonth() &&
                  busyDate.getFullYear() === date.getFullYear()
                )}
              />
            </div>
            <p className="text-center mt-4 text-blue-600">
              白色の日付が予約可能です。グレーの日付は予約済みです。
            </p>
          </div>
        </section>
        <section id="testimonials" className="w-full py-12 md:py-24 lg:py-32 bg-white">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-12 text-blue-800">
              お客様の声
            </h2>
            <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
              <div className="flex flex-col items-center text-center">
                <img
                  alt="Customer"
                  className="rounded-full mb-4"
                  height="80"
                  src="/placeholder.svg"
                  style={{
                    aspectRatio: "80/80",
                    objectFit: "cover",
                  }}
                  width="80"
                />
                <p className="text-blue-600 mb-2">
                  "エアコンがこんなにきれいになるなんて驚きました。部屋の空気が変わった気がします！"
                </p>
                <p className="font-semibold text-blue-800">田中さん</p>
              </div>
              <div className="flex flex-col items-center text-center">
                <img
                  alt="Customer"
                  className="rounded-full mb-4"
                  height="80"
                  src="/placeholder.svg"
                  style={{
                    aspectRatio: "80/80",
                    objectFit: "cover",
                  }}
                  width="80"
                />
                <p className="text-blue-600 mb-2">
                  "レンジフードの油汚れが完全に取れて、キッチンが明るくなりました。プロの技術に感謝です。"
                </p>
                <p className="font-semibold text-blue-800">佐藤さん</p>
              </div>
              <div className="flex flex-col items-center text-center">
                <img
                  alt="Customer"
                  className="rounded-full mb-4"
                  height="80"
                  src="/placeholder.svg"
                  style={{
                    aspectRatio: "80/80",
                    objectFit: "cover",
                  }}
                  width="80"
                />
                <p className="text-blue-600 mb-2">
                  "定期的に利用していますが、毎回丁寧な仕事に満足しています。家族みんなが快適に過ごせています。"
                </p>
                <p className="font-semibold text-blue-800">鈴木さん</p>
              </div>
            </div>
          </div>
        </section>
        <section id="contact" className="w-full py-12 md:py-24 lg:py-32 bg-blue-100">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-12 text-blue-800">
              お問い合わせ
            </h2>
            <div className="max-w-2xl mx-auto">
              <form className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">お名前</Label>
                  <Input id="name" placeholder="山田 太郎" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">メールアドレス</Label>
                  <Input id="email" placeholder="taro@example.com" required type="email" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="message">メッセージ</Label>
                  <Textarea className="min-h-[100px]" id="message" placeholder="お問い合わせ内容をご記入ください" required />
                </div>
                <Button className="w-full bg-blue-600 hover:bg-blue-700" type="submit">
                  送信
                </Button>
              </form>
            </div>
          </div>
        </section>
      </main>
      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t bg-blue-600 text-white">
        <p className="text-xs">© 2024 ハタハタ クリーニングサービス. All rights reserved.</p>
        <nav className="sm:ml-auto flex gap-4 sm:gap-6">
          <Link className="text-xs hover:underline underline-offset-4" href="#">
            プライバシーポリシー
          </Link>
          <Link className="text-xs hover:underline underline-offset-4" href="#">
            利用規約
          </Link>
        </nav>
      </footer>
    </div>
  )
}